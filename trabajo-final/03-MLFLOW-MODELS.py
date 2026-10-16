# Databricks notebook source
from pyspark.sql import functions as F

TRAIN_TABLE = "workspace.bigdata_milagros_1.tp_final_train"
TEST_TABLE = "workspace.bigdata_milagros_1.tp_final_test"

train_df = spark.table(TRAIN_TABLE)
test_df = spark.table(TEST_TABLE)

print(f"Train: {train_df.count():,}")
print(f"Test: {test_df.count():,}")

train_df.printSchema()

# COMMAND ----------

import mlflow
import mlflow.spark

from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import (
    BinaryClassificationEvaluator,
    MulticlassClassificationEvaluator
)

# COMMAND ----------

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

lr = LogisticRegression(
    featuresCol="features",
    labelCol="DEFAULT",
    maxIter=100,
    regParam=0.0,
    elasticNetParam=0.0
)

with mlflow.start_run(run_name="logistic_regression_baseline"):

    lr_model = lr.fit(train_df)

    predictions = lr_model.transform(test_df)

    roc_auc = roc_evaluator.evaluate(predictions)
    pr_auc = pr_evaluator.evaluate(predictions)
    accuracy = accuracy_evaluator.evaluate(predictions)
    f1 = f1_evaluator.evaluate(predictions)

    # Parámetros
    mlflow.log_param("model", "LogisticRegression")
    mlflow.log_param("maxIter", 100)
    mlflow.log_param("regParam", 0.0)
    mlflow.log_param("elasticNetParam", 0.0)
    mlflow.log_param("split_method", "xxhash64_ID_mod100")

    # Métricas
    mlflow.log_metric("roc_auc", roc_auc)
    mlflow.log_metric("pr_auc", pr_auc)
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("f1", f1)

    print("Logistic Regression — Baseline")
    print(f"ROC-AUC:  {roc_auc:.4f}")
    print(f"PR-AUC:   {pr_auc:.4f}")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"F1:       {f1:.4f}")

# COMMAND ----------

from pyspark.ml.classification import RandomForestClassifier
rf = RandomForestClassifier(
    featuresCol="features",
    labelCol="DEFAULT",
    numTrees=100,
    maxDepth=5,
    seed=42
)

with mlflow.start_run(run_name="random_forest_baseline"):

    rf_model = rf.fit(train_df)

    rf_predictions = rf_model.transform(test_df)

    roc_auc_rf = roc_evaluator.evaluate(rf_predictions)
    pr_auc_rf = pr_evaluator.evaluate(rf_predictions)
    accuracy_rf = accuracy_evaluator.evaluate(rf_predictions)
    f1_rf = f1_evaluator.evaluate(rf_predictions)

    # Parámetros
    mlflow.log_param("model", "RandomForest")
    mlflow.log_param("numTrees", 100)
    mlflow.log_param("maxDepth", 5)
    mlflow.log_param("seed", 42)
    mlflow.log_param("split_method","xxhash64_ID_mod100")

    # Métricas
    mlflow.log_metric("roc_auc", roc_auc_rf)
    mlflow.log_metric("pr_auc", pr_auc_rf)
    mlflow.log_metric("accuracy", accuracy_rf)
    mlflow.log_metric("f1", f1_rf)

    print("Random Forest — Baseline")
    print(f"ROC-AUC:  {roc_auc_rf:.4f}")
    print(f"PR-AUC:   {pr_auc_rf:.4f}")
    print(f"Accuracy: {accuracy_rf:.4f}")
    print(f"F1:       {f1_rf:.4f}")

# COMMAND ----------

from pyspark.ml.classification import GBTClassifier
gbt = GBTClassifier(
    featuresCol="features",
    labelCol="DEFAULT",
    maxIter=50,
    maxDepth=5,
    stepSize=0.1,
    seed=42
)

with mlflow.start_run(run_name="gradient_boosted_trees_baseline"):

    gbt_model = gbt.fit(train_df)

    gbt_predictions = gbt_model.transform(test_df)

    roc_auc_gbt = roc_evaluator.evaluate(gbt_predictions)
    pr_auc_gbt = pr_evaluator.evaluate(gbt_predictions)
    accuracy_gbt = accuracy_evaluator.evaluate(gbt_predictions)
    f1_gbt = f1_evaluator.evaluate(gbt_predictions)

    # Parámetros
    mlflow.log_param("model", "GBTClassifier")
    mlflow.log_param("maxIter", 50)
    mlflow.log_param("maxDepth", 5)
    mlflow.log_param("stepSize", 0.1)
    mlflow.log_param("seed", 42)
    mlflow.log_param("split_method", "xxhash64_ID_mod100")

    # Métricas
    mlflow.log_metric("roc_auc", roc_auc_gbt)
    mlflow.log_metric("pr_auc", pr_auc_gbt)
    mlflow.log_metric("accuracy", accuracy_gbt)
    mlflow.log_metric("f1", f1_gbt)

    print("Gradient-Boosted Trees — Baseline")
    print(f"ROC-AUC:  {roc_auc_gbt:.4f}")
    print(f"PR-AUC:   {pr_auc_gbt:.4f}")
    print(f"Accuracy: {accuracy_gbt:.4f}")
    print(f"F1:       {f1_gbt:.4f}")



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

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    f1_positive = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0
    )

    return {
        "TP": tp,
        "FP": fp,
        "FN": fn,
        "TN": tn,
        "precision": precision,
        "recall": recall,
        "f1_positive": f1_positive
    }

# COMMAND ----------

lr_class_metrics = positive_class_metrics(predictions)
rf_class_metrics = positive_class_metrics(rf_predictions)
gbt_class_metrics = positive_class_metrics(gbt_predictions)

print("LOGISTIC REGRESSION")
print(lr_class_metrics)

print("\nRANDOM FOREST")
print(rf_class_metrics)

print("\nGRADIENT-BOOSTED TREES")
print(gbt_class_metrics)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conclusiones de los modelos baseline
# MAGIC
# MAGIC Se entrenaron y compararon tres modelos de clasificación utilizando el mismo conjunto de entrenamiento y prueba y la misma representación de variables: Logistic Regression, Random Forest y Gradient-Boosted Trees (GBT). Todos los experimentos fueron registrados mediante MLflow utilizando un conjunto común de métricas para garantizar una comparación consistente.
# MAGIC
# MAGIC | Modelo | ROC-AUC | PR-AUC | Accuracy | F1 ponderado |
# MAGIC |---|---:|---:|---:|---:|
# MAGIC | Logistic Regression | 0.7263 | 0.5028 | 0.8150 | 0.7777 |
# MAGIC | Random Forest | 0.7786 | 0.5460 | 0.8170 | 0.7868 |
# MAGIC | Gradient-Boosted Trees | **0.7881** | **0.5500** | **0.8255** | **0.8074** |
# MAGIC
# MAGIC El modelo GBT obtuvo el mejor desempeño global entre los tres modelos baseline, superando a Logistic Regression y Random Forest en ROC-AUC, PR-AUC, accuracy y F1 ponderado.
# MAGIC
# MAGIC Dado que la variable objetivo presenta un desbalance moderado, también se analizaron métricas específicas para la clase positiva ('DEFAULT = 1').
# MAGIC
# MAGIC | Modelo | Precision | Recall | F1 clase positiva |
# MAGIC |---|---:|---:|---:|
# MAGIC | Logistic Regression | 0.7241 | 0.2498 | 0.3715 |
# MAGIC | Random Forest | 0.6930 | 0.2940 | 0.4128 |
# MAGIC | Gradient-Boosted Trees | **0.6732** | **0.3938** | **0.4969** |
# MAGIC
# MAGIC GBT identificó correctamente 517 de los 1.313 casos reales de default, frente a 386 detectados por Random Forest y 328 por Logistic Regression. Sin embargo, con el umbral de clasificación estándar todavía quedaron 796 casos de default clasificados como no-default.
# MAGIC
# MAGIC Por lo tanto, GBT se selecciona como el mejor modelo baseline para continuar la experimentación. En la siguiente etapa se evaluarán diferentes configuraciones de hiperparámetros y posteriormente se analizará el efecto del umbral de clasificación sobre el trade-off entre precision y recall.