# Databricks notebook source
from pyspark.sql import functions as F

TRAIN_TABLE = "workspace.bigdata_milagros_1.tp_final_train"
TEST_TABLE = "workspace.bigdata_milagros_1.tp_final_test"

train_df = spark.table(TRAIN_TABLE)
test_df = spark.table(TEST_TABLE)

print(f"Train: {train_df.count():,}")
print(f"Test: {test_df.count():,}")

# COMMAND ----------

import mlflow

from pyspark.ml.classification import GBTClassifier
from pyspark.ml.evaluation import (
    BinaryClassificationEvaluator,
    MulticlassClassificationEvaluator
)

experiment_name = "/Shared/tp_final_default_mlflow"
mlflow.set_experiment(experiment_name)

print(f"Experimento MLflow: {experiment_name}")

# COMMAND ----------

roc_evaluator = BinaryClassificationEvaluator(
    labelCol="DEFAULT",
    rawPredictionCol="rawPrediction",
    metricName="areaUnderROC"
)

pr_evaluator = BinaryClassificationEvaluator(
    labelCol="DEFAULT",
    rawPredictionCol="rawPrediction",
    metricName="areaUnderPR"
)

accuracy_evaluator = MulticlassClassificationEvaluator(
    labelCol="DEFAULT",
    predictionCol="prediction",
    metricName="accuracy"
)

f1_evaluator = MulticlassClassificationEvaluator(
    labelCol="DEFAULT",
    predictionCol="prediction",
    metricName="f1"
)

# COMMAND ----------

def positive_class_metrics(predictions):

    tp = predictions.filter(
        (F.col("DEFAULT") == 1) & (F.col("prediction") == 1)
    ).count()

    fp = predictions.filter(
        (F.col("DEFAULT") == 0) & (F.col("prediction") == 1)
    ).count()

    fn = predictions.filter(
        (F.col("DEFAULT") == 1) & (F.col("prediction") == 0)
    ).count()

    tn = predictions.filter(
        (F.col("DEFAULT") == 0) & (F.col("prediction") == 0)
    ).count()

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0

    f1_positive = (
        2 * precision * recall / (precision + recall)
        if (precision + recall)
        else 0
    )

    return {
        "TP": tp,
        "FP": fp,
        "FN": fn,
        "TN": tn,
        "precision_positive": precision,
        "recall_positive": recall,
        "f1_positive": f1_positive
    }

# COMMAND ----------

fit_df, validation_df = train_df.randomSplit(
    [0.8, 0.2],
    seed=42
)

print(f"Train para tuning: {fit_df.count():,}")
print(f"Validation: {validation_df.count():,}")
print(f"Test reservado: {test_df.count():,}")

# COMMAND ----------

gbt_configs = [
    {"name": "gbt_depth3", "maxDepth": 3, "maxIter": 50, "stepSize": 0.10},
    {"name": "gbt_baseline", "maxDepth": 5, "maxIter": 50, "stepSize": 0.10},
    {"name": "gbt_iter100", "maxDepth": 5, "maxIter": 100, "stepSize": 0.05},
    {"name": "gbt_depth7", "maxDepth": 7, "maxIter": 50, "stepSize": 0.10}
]

for config in gbt_configs:
    print(config)

# COMMAND ----------

results = []

for config in gbt_configs:

    print(f"\nEntrenando: {config['name']}...")

    gbt = GBTClassifier(
        featuresCol="features",
        labelCol="DEFAULT",
        maxDepth=config["maxDepth"],
        maxIter=config["maxIter"],
        stepSize=config["stepSize"],
        seed=42
    )

    with mlflow.start_run(run_name=f"tuning_{config['name']}"):

        # Entrenamiento
        model = gbt.fit(fit_df)

        # Predicciones
        preds = model.transform(validation_df)

        # Métricas globales
        roc_auc = roc_evaluator.evaluate(preds)
        pr_auc = pr_evaluator.evaluate(preds)
        accuracy = accuracy_evaluator.evaluate(preds)
        f1_weighted = f1_evaluator.evaluate(preds)

        # Métricas específicas DEFAULT = 1
        positive_metrics = positive_class_metrics(preds)

        # Registrar parámetros en MLflow
        mlflow.log_param("model", "GBTClassifier")
        mlflow.log_param("maxDepth", config["maxDepth"])
        mlflow.log_param("maxIter", config["maxIter"])
        mlflow.log_param("stepSize", config["stepSize"])
        mlflow.log_param("seed", 42)
        mlflow.log_param("evaluation_set", "validation")
        mlflow.log_param("validation_split_seed", 42)

        # Registrar métricas en MLflow
        mlflow.log_metric("roc_auc", roc_auc)
        mlflow.log_metric("pr_auc", pr_auc)
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("f1_weighted", f1_weighted)

        mlflow.log_metric(
            "precision_positive",
            positive_metrics["precision_positive"]
        )

        mlflow.log_metric(
            "recall_positive",
            positive_metrics["recall_positive"]
        )

        mlflow.log_metric(
            "f1_positive",
            positive_metrics["f1_positive"]
        )

        # Guardar resultados para comparación
        results.append({
            "model": config["name"],
            "maxDepth": config["maxDepth"],
            "maxIter": config["maxIter"],
            "stepSize": config["stepSize"],
            "roc_auc": roc_auc,
            "pr_auc": pr_auc,
            "accuracy": accuracy,
            "f1_weighted": f1_weighted,
            "precision_positive": positive_metrics["precision_positive"],
            "recall_positive": positive_metrics["recall_positive"],
            "f1_positive": positive_metrics["f1_positive"]
        })

        print(
            f"ROC-AUC={roc_auc:.4f} | "
            f"PR-AUC={pr_auc:.4f} | "
            f"Recall+={positive_metrics['recall_positive']:.4f} | "
            f"F1+={positive_metrics['f1_positive']:.4f}"
        )

# COMMAND ----------

import pandas as pd

results_pd = pd.DataFrame(results)

results_pd = results_pd.sort_values(
    by="pr_auc",
    ascending=False
).reset_index(drop=True)

display(results_pd)

# COMMAND ----------

best_gbt = GBTClassifier(
    featuresCol="features",
    labelCol="DEFAULT",
    maxDepth=3,
    maxIter=50,
    stepSize=0.1,
    seed=42
)

best_gbt_model = best_gbt.fit(fit_df)
best_predictions = best_gbt_model.transform(validation_df)

print("Modelo candidato listo ✅")

# COMMAND ----------

from pyspark.ml.functions import vector_to_array

threshold_df = (
    best_predictions
    .withColumn(
        "prob_default",
        vector_to_array("probability")[1]
    )
    .select("DEFAULT", "prob_default")
)

display(threshold_df.limit(10))

# COMMAND ----------

thresholds = [
    0.20, 0.25, 0.30, 0.35,
    0.40, 0.45, 0.50, 0.55, 0.60
]

threshold_results = []

for threshold in thresholds:

    evaluated = threshold_df.withColumn(
        "prediction_threshold",
        (F.col("prob_default") >= threshold).cast("int")
    )

    tp = evaluated.filter(
        (F.col("DEFAULT") == 1) &
        (F.col("prediction_threshold") == 1)
    ).count()

    fp = evaluated.filter(
        (F.col("DEFAULT") == 0) &
        (F.col("prediction_threshold") == 1)
    ).count()

    fn = evaluated.filter(
        (F.col("DEFAULT") == 1) &
        (F.col("prediction_threshold") == 0)
    ).count()

    tn = evaluated.filter(
        (F.col("DEFAULT") == 0) &
        (F.col("prediction_threshold") == 0)
    ).count()

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0
    )

    threshold_results.append({
        "threshold": threshold,
        "precision": precision,
        "recall": recall,
        "f1_positive": f1,
        "TP": tp,
        "FP": fp,
        "FN": fn,
        "TN": tn
    })

# COMMAND ----------

threshold_results_pd = pd.DataFrame(threshold_results)

display(
    threshold_results_pd.sort_values(
        "threshold"
    )
)

# COMMAND ----------

best_threshold_row = threshold_results_pd.loc[
    threshold_results_pd["f1_positive"].idxmax()
]

best_threshold = float(best_threshold_row["threshold"])

print(f"Mejor threshold según F1 positivo: {best_threshold:.2f}")
print(f"Precision: {best_threshold_row['precision']:.4f}")
print(f"Recall:    {best_threshold_row['recall']:.4f}")
print(f"F1+:       {best_threshold_row['f1_positive']:.4f}")

# COMMAND ----------

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))

plt.plot(
    threshold_results_pd["threshold"],
    threshold_results_pd["precision"],
    marker="o",
    label="Precision",
    color="#B8D8F0"
)

plt.plot(
    threshold_results_pd["threshold"],
    threshold_results_pd["recall"],
    marker="o",
    label="Recall",
    color="#F4B6C2"
)

plt.plot(
    threshold_results_pd["threshold"],
    threshold_results_pd["f1_positive"],
    marker="o",
    label="F1 clase positiva",
    color="#CDB4DB"
)

plt.axvline(
    x=best_threshold,
    linestyle="--",
    color="#A8DADC",
    label=f"Threshold seleccionado = {best_threshold:.2f}"
)

plt.title("Impacto del threshold sobre las métricas de DEFAULT = 1")
plt.xlabel("Threshold")
plt.ylabel("Métrica")
plt.ylim(0, 0.8)
plt.legend()
plt.grid(alpha=0.2)

plt.tight_layout()
plt.show()

# COMMAND ----------

from pyspark.ml.classification import GBTClassifier
from pyspark.ml.functions import vector_to_array


final_gbt = GBTClassifier(
    featuresCol="features",
    labelCol="DEFAULT",
    maxDepth=3,
    maxIter=50,
    stepSize=0.1,
    seed=42
)

final_gbt_model = final_gbt.fit(train_df)

final_test_predictions = final_gbt_model.transform(test_df)

final_test_predictions = (
    final_test_predictions
    .withColumn(
        "prob_default",
        vector_to_array("probability")[1]
    )
    .withColumn(
        "prediction_final",
        (F.col("prob_default") >= best_threshold).cast("int")
    )
)

print(f"Threshold seleccionado en validation: {best_threshold:.2f}")
print("Modelo final evaluado sobre TEST ✅")

# COMMAND ----------

confusion_matrix = (
    final_test_predictions
    .groupBy("DEFAULT", "prediction_final")
    .count()
    .orderBy("DEFAULT", "prediction_final")
)

display(confusion_matrix)

# COMMAND ----------

# ============================================================
# MÉTRICAS FINALES SOBRE TEST
# ============================================================

tp = final_test_predictions.filter(
    (F.col("DEFAULT") == 1) &
    (F.col("prediction_final") == 1)
).count()

fp = final_test_predictions.filter(
    (F.col("DEFAULT") == 0) &
    (F.col("prediction_final") == 1)
).count()

fn = final_test_predictions.filter(
    (F.col("DEFAULT") == 1) &
    (F.col("prediction_final") == 0)
).count()

tn = final_test_predictions.filter(
    (F.col("DEFAULT") == 0) &
    (F.col("prediction_final") == 0)
).count()

precision_final = tp / (tp + fp) if (tp + fp) else 0
recall_final = tp / (tp + fn) if (tp + fn) else 0

f1_final = (
    2 * precision_final * recall_final /
    (precision_final + recall_final)
    if (precision_final + recall_final) else 0
)

accuracy_final = (tp + tn) / (tp + tn + fp + fn)

# ROC-AUC y PR-AUC usan las probabilidades del modelo,
# por lo que no dependen del threshold elegido.
roc_auc_final = roc_evaluator.evaluate(final_test_predictions)
pr_auc_final = pr_evaluator.evaluate(final_test_predictions)

print("RESULTADOS FINALES - TEST")
print(f"ROC-AUC:   {roc_auc_final:.4f}")
print(f"PR-AUC:    {pr_auc_final:.4f}")
print(f"Accuracy:  {accuracy_final:.4f}")
print(f"Precision+: {precision_final:.4f}")
print(f"Recall+:    {recall_final:.4f}")
print(f"F1+:        {f1_final:.4f}")
print(f"TP={tp} | FP={fp} | FN={fn} | TN={tn}")


# ============================================================
# REGISTRO FINAL EN MLFLOW
# ============================================================

with mlflow.start_run(run_name="GBT_FINAL_TEST_threshold_030"):

    mlflow.log_param("model", "GBTClassifier")
    mlflow.log_param("maxDepth", 3)
    mlflow.log_param("maxIter", 50)
    mlflow.log_param("stepSize", 0.1)
    mlflow.log_param("seed", 42)

    mlflow.log_param("threshold", best_threshold)
    mlflow.log_param(
        "threshold_selection",
        "max_f1_positive_on_validation"
    )
    mlflow.log_param(
        "model_selection",
        "max_pr_auc_on_validation"
    )
    mlflow.log_param(
        "final_evaluation_set",
        "test"
    )

    mlflow.log_metric("roc_auc", roc_auc_final)
    mlflow.log_metric("pr_auc", pr_auc_final)
    mlflow.log_metric("accuracy", accuracy_final)

    mlflow.log_metric(
        "precision_positive",
        precision_final
    )
    mlflow.log_metric(
        "recall_positive",
        recall_final
    )
    mlflow.log_metric(
        "f1_positive",
        f1_final
    )

    mlflow.log_metric("true_positives", tp)
    mlflow.log_metric("false_positives", fp)
    mlflow.log_metric("false_negatives", fn)
    mlflow.log_metric("true_negatives", tn)

print("Resultados finales de TEST registrados en MLflow ✅")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Resultado final
# MAGIC
# MAGIC La selección de hiperparámetros se realizó utilizando un conjunto de validación separado del conjunto de test. De acuerdo con PR-AUC, se seleccionó un Gradient-Boosted Trees con `maxDepth=3`, `maxIter=50` y `stepSize=0.1`.
# MAGIC
# MAGIC Posteriormente, el threshold de clasificación se seleccionó sobre validation maximizando el F1 de la clase positiva, obteniéndose un threshold de `0.30`.
# MAGIC
# MAGIC Una vez finalizada la selección, el modelo fue reentrenado utilizando el conjunto de entrenamiento completo y evaluado una única vez sobre el conjunto de test reservado.
# MAGIC
# MAGIC ### Resultados finales sobre test
# MAGIC
# MAGIC - ROC-AUC: **0.7884**
# MAGIC - PR-AUC: **0.5573**
# MAGIC - Accuracy: **0.8043**
# MAGIC - Precision (DEFAULT=1): **0.5566**
# MAGIC - Recall (DEFAULT=1): **0.5202**
# MAGIC - F1 (DEFAULT=1): **0.5378**
# MAGIC
# MAGIC Matriz de confusión:
# MAGIC
# MAGIC - TP: **683**
# MAGIC - FP: **544**
# MAGIC - FN: **630**
# MAGIC - TN: **4142**
# MAGIC
# MAGIC El ajuste del threshold desde 0.50 a 0.30 permitió priorizar la detección de clientes con default, aceptando como contrapartida un aumento de falsos positivos. Esta decisión resulta coherente con el objetivo de prestar especial atención a la clase positiva y con el desbalance observado en el dataset.
# MAGIC
# MAGIC Como limitaciones, los resultados corresponden a un único dataset y a un conjunto acotado de configuraciones. Futuras extensiones podrían incorporar una búsqueda de hiperparámetros más amplia, validación cruzada y otros algoritmos.

# COMMAND ----------

import mlflow
import pandas as pd
import tempfile
import os

# Tablas que queremos guardar como evidencia
threshold_artifact = pd.DataFrame(threshold_results)

confusion_artifact = pd.DataFrame({
    "actual": [0, 0, 1, 1],
    "predicted": [0, 1, 0, 1],
    "count": [tn, fp, fn, tp]
})

with tempfile.TemporaryDirectory() as tmpdir:

    threshold_path = os.path.join(
        tmpdir,
        "threshold_comparison.csv"
    )

    confusion_path = os.path.join(
        tmpdir,
        "confusion_matrix_test.csv"
    )

    threshold_artifact.to_csv(
        threshold_path,
        index=False
    )

    confusion_artifact.to_csv(
        confusion_path,
        index=False
    )

    with mlflow.start_run(
        run_name="GBT_FINAL_ARTIFACTS_threshold_030"
    ):

        mlflow.log_param("model", "GBTClassifier")
        mlflow.log_param("threshold", best_threshold)

        mlflow.log_artifact(
            threshold_path,
            artifact_path="evaluation"
        )

        mlflow.log_artifact(
            confusion_path,
            artifact_path="evaluation"
        )

print("Artifacts registrados en MLflow ✅")