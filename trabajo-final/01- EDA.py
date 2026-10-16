# Databricks notebook source
from pyspark.sql import functions as F

DATA_PATH = "/Volumes/workspace/bigdata_milagros_1/tp_final_data/default of credit card clients.csv"

df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .option("sep", ";") 
    .csv(DATA_PATH)
)

display(df)

# COMMAND ----------

#objetivo eliminar la primer fila 
header_row = df.first()

real_columns = [str(header_row[c]) for c in df.columns]
df = df.filter(F.col("_c0") != "ID")
for old_name, new_name in zip(df.columns, real_columns):
    df = df.withColumnRenamed(old_name, new_name)

display(df)

# COMMAND ----------

# Dimensiones del dataset
n_rows = df.count()
n_cols = len(df.columns)

print(f"Cantidad de registros: {n_rows:,}")
print(f"Cantidad de columnas: {n_cols}")

# Esquema
df.printSchema()

# COMMAND ----------

# Conversión de variables a tipo numérico
for column in df.columns:
    df = df.withColumn(column, F.col(column).cast("int"))

df.printSchema()

# COMMAND ----------

# Valores nulos por columna
null_counts = df.select([
    F.sum(F.col(c).isNull().cast("int")).alias(c)
    for c in df.columns
])

display(null_counts)

# Duplicados
total_rows = df.count()
unique_rows = df.dropDuplicates().count()

print(f"Registros totales: {total_rows:,}")
print(f"Registros duplicados: {total_rows - unique_rows:,}")

# Verificar unicidad del ID
unique_ids = df.select("ID").distinct().count()

print(f"IDs únicos: {unique_ids:,}")

# COMMAND ----------

categorical_cols = ["SEX", "EDUCATION", "MARRIAGE"]

for c in categorical_cols:
    print(f"\n--- {c} ---")
    df.groupBy(c).count().orderBy(c).show()

# COMMAND ----------

print(df.columns)

# COMMAND ----------

#renombro target para practicidad
df = df.withColumnRenamed(
    "default payment next month",
    "DEFAULT"
)

# COMMAND ----------

total = df.count()

target_distribution = (
    df.groupBy("DEFAULT")
      .count()
      .withColumn(
          "percentage",
          F.round(F.col("count") / F.lit(total) * 100, 2)
      )
      .orderBy("DEFAULT")
)

display(target_distribution)

# COMMAND ----------

import matplotlib.pyplot as plt

target_pd = (
    target_distribution
    .orderBy("DEFAULT")
    .toPandas()
)

labels = ["No Default", "Default"]

plt.figure(figsize=(8, 5))

bars = plt.bar(
    labels,
    target_pd["percentage"],
    color=["#B8D8F0", "#F4B6C2"]
)

plt.title("Distribución de la variable objetivo")
plt.ylabel("Porcentaje de clientes (%)")
plt.xlabel("Estado de default")
plt.ylim(0, 100)

for bar, pct in zip(bars, target_pd["percentage"]):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 1,
        f"{pct:.2f}%",
        ha="center",
        fontsize=11
    )

plt.tight_layout()
plt.show()

# COMMAND ----------

df.select(
    "LIMIT_BAL",
    "AGE",
    "BILL_AMT1",
    "PAY_AMT1"
).summary(
    "count", "mean", "stddev", "min", "25%", "50%", "75%", "max"
).show()

# COMMAND ----------

limit_by_default = (
    df.groupBy("DEFAULT")
      .agg(
          F.count("*").alias("clientes"),
          F.round(F.avg("LIMIT_BAL"), 2).alias("limite_promedio"),
          F.expr("percentile_approx(LIMIT_BAL, 0.5)").alias("limite_mediano")
      )
      .orderBy("DEFAULT")
)

display(limit_by_default)

# COMMAND ----------

age_by_default = (
    df.groupBy("DEFAULT")
      .agg(
          F.round(F.avg("AGE"), 2).alias("edad_promedio"),
          F.expr("percentile_approx(AGE, 0.5)").alias("edad_mediana"),
          F.min("AGE").alias("edad_minima"),
          F.max("AGE").alias("edad_maxima")
      )
      .orderBy("DEFAULT")
)

display(age_by_default)

# COMMAND ----------

pay0_default = (
    df.groupBy("PAY_0")
      .agg(
          F.count("*").alias("clientes"),
          F.sum("DEFAULT").alias("defaults"),
          F.round(F.avg("DEFAULT") * 100, 2).alias("tasa_default")
      )
      .orderBy("PAY_0")
)

display(pay0_default)

# COMMAND ----------

pay0_pd = pay0_default.toPandas()

plt.figure(figsize=(10, 5))

bars = plt.bar(
    pay0_pd["PAY_0"].astype(str),
    pay0_pd["tasa_default"],
    color="#CDB4DB"
)

plt.title("Tasa de default según estado de pago más reciente")
plt.xlabel("Estado de pago (PAY_0)")
plt.ylabel("Tasa de default (%)")

for bar, value in zip(bars, pay0_pd["tasa_default"]):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.8,
        f"{value:.1f}%",
        ha="center",
        fontsize=9
    )

plt.tight_layout()
plt.show()

# COMMAND ----------

for c in ["SEX", "EDUCATION", "MARRIAGE"]:
    
    print(f"\n--- Tasa de default por {c} ---")
    
    result = (
        df.groupBy(c)
          .agg(
              F.count("*").alias("clientes"),
              F.sum("DEFAULT").alias("defaults"),
              F.round(F.avg("DEFAULT") * 100, 2).alias("tasa_default")
          )
          .orderBy(c)
    )
    
    result.show()

# COMMAND ----------

df_limit = (
    df.withColumn(
        "LIMIT_RANGE",
        F.when(F.col("LIMIT_BAL") <= 50000, "1. <= 50k")
         .when(F.col("LIMIT_BAL") <= 100000, "2. 50k-100k")
         .when(F.col("LIMIT_BAL") <= 200000, "3. 100k-200k")
         .when(F.col("LIMIT_BAL") <= 300000, "4. 200k-300k")
         .otherwise("5. > 300k")
    )
)

limit_default = (
    df_limit.groupBy("LIMIT_RANGE")
            .agg(
                F.count("*").alias("clientes"),
                F.round(F.avg("DEFAULT") * 100, 2).alias("tasa_default")
            )
            .orderBy("LIMIT_RANGE")
)

display(limit_default)

# COMMAND ----------

limit_pd = limit_default.toPandas()

plt.figure(figsize=(10, 5))

bars = plt.bar(
    limit_pd["LIMIT_RANGE"],
    limit_pd["tasa_default"],
    color="#A8DADC"
)

plt.title("Tasa de default según límite de crédito")
plt.xlabel("Rango de límite de crédito")
plt.ylabel("Tasa de default (%)")

for bar, value in zip(bars, limit_pd["tasa_default"]):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.5,
        f"{value:.1f}%",
        ha="center",
        fontsize=9
    )

plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conclusiones del análisis exploratorio
# MAGIC
# MAGIC El conjunto de datos contiene 30.000 clientes y 25 variables, incluyendo la variable objetivo 'DEFAULT'. No se detectaron valores nulos ni registros duplicados, y el identificador 'ID' es único para cada observación.
# MAGIC
# MAGIC La variable objetivo presenta un desbalance moderado: el 77,88% de los clientes no registró default, mientras que el 22,12% sí lo hizo. Debido a este desbalance, la evaluación de los modelos no se basará únicamente en accuracy, sino también en métricas como precision, recall, F1 y ROC-AUC.
# MAGIC
# MAGIC La edad presenta valores similares entre ambos grupos, con una edad promedio de 35,42 años para clientes sin default y 35,73 años para clientes con default, por lo que no se observa una separación relevante a nivel descriptivo.
# MAGIC
# MAGIC En cambio, el límite de crédito muestra diferencias más marcadas. Los clientes sin default presentan un límite promedio de 178.099,73, frente a 130.109,66 entre los clientes con default. Además, la tasa de default disminuye progresivamente desde 31,79% para límites de hasta 50.000 hasta 13,26% para límites superiores a 300.000.
# MAGIC
# MAGIC El estado de pago más reciente ('PAY_0') presenta una fuerte asociación con la variable objetivo. La tasa de default es de 12,81% para clientes sin atraso ('PAY_0 = 0'), aumenta a 33,95% para 'PAY_0 = 1' y alcanza 69,14% para 'PAY_0 = 2'. Las categorías de mora más elevada presentan pocos registros, por lo que sus porcentajes deben interpretarse con cautela.
# MAGIC
# MAGIC Finalmente, se identificaron categorías no documentadas o residuales en 'EDUCATION' (0, 5 y 6) y 'MARRIAGE' (0). Estas observaciones se conservarán y serán agrupadas dentro de una categoría 'OTHER/UNKNOWN' durante la etapa de preprocessing.