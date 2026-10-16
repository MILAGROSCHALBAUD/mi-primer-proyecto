# Databricks notebook source
from pyspark.sql import functions as F

DATA_PATH = "/Volumes/workspace/bigdata_milagros_1/tp_final_data/default of credit card clients.csv"

df_raw = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .option("sep", ";")
    .csv(DATA_PATH)
)

print(f"Registros originales: {df_raw.count():,}")

# COMMAND ----------

header_row = df_raw.first()

real_columns = [str(header_row[c]) for c in df_raw.columns]

df = df_raw.filter(F.col("_c0") != "ID")

for old_name, new_name in zip(df.columns, real_columns):
    df = df.withColumnRenamed(old_name, new_name)

# Conversión a numérico
for column in df.columns:
    df = df.withColumn(column, F.col(column).cast("int"))

# Renombrar target
df = df.withColumnRenamed(
    "default payment next month",
    "DEFAULT"
)

print(f"Registros luego de la carga: {df.count():,}")
df.printSchema()

# COMMAND ----------

df = (
    df
    .withColumn(
        "EDUCATION",
        F.when(F.col("EDUCATION").isin(0, 5, 6), 4)
         .otherwise(F.col("EDUCATION"))
    )
    .withColumn(
        "MARRIAGE",
        F.when(F.col("MARRIAGE") == 0, 3)
         .otherwise(F.col("MARRIAGE"))
    )
)

# COMMAND ----------

df.groupBy("EDUCATION").count().orderBy("EDUCATION").show()
df.groupBy("MARRIAGE").count().orderBy("MARRIAGE").show()

# COMMAND ----------

categorical_cols = [
    "SEX",
    "EDUCATION",
    "MARRIAGE"
]

excluded_cols = [
    "ID",
    "DEFAULT"
]

numerical_cols = [
    c for c in df.columns
    if c not in categorical_cols + excluded_cols
]

print("Variables categóricas:")
print(categorical_cols)

print("\nVariables numéricas:")
print(numerical_cols)

print(f"\nCantidad categóricas: {len(categorical_cols)}")
print(f"Cantidad numéricas: {len(numerical_cols)}")
print(f"Total features originales: {len(categorical_cols) + len(numerical_cols)}")

# COMMAND ----------

from pyspark.ml import Pipeline
from pyspark.ml.feature import (
    StringIndexer,
    OneHotEncoder,
    VectorAssembler
)

# Indexar variables categóricas
indexers = [
    StringIndexer(
        inputCol=c,
        outputCol=f"{c}_index",
        handleInvalid="keep"
    )
    for c in categorical_cols
]

# One-Hot Encoding
encoder = OneHotEncoder(
    inputCols=[f"{c}_index" for c in categorical_cols],
    outputCols=[f"{c}_ohe" for c in categorical_cols],
    handleInvalid="keep"
)

# Columnas que entrarán al modelo
assembler_inputs = (
    numerical_cols +
    [f"{c}_ohe" for c in categorical_cols]
)

assembler = VectorAssembler(
    inputCols=assembler_inputs,
    outputCol="features",
    handleInvalid="keep"
)

preprocessing_pipeline = Pipeline(
    stages=indexers + [encoder, assembler]
)

# COMMAND ----------

# Split determinístico 80/20 basado en ID
# El mismo ID siempre pertenecerá al mismo conjunto.

df_split = df.withColumn(
    "_split",
    F.pmod(F.xxhash64(F.col("ID")), F.lit(100))
)

train_df = df_split.filter(F.col("_split") < 80).drop("_split")
test_df = df_split.filter(F.col("_split") >= 80).drop("_split")

print(f"Train: {train_df.count():,}")
print(f"Test: {test_df.count():,}")
print(f"Total: {train_df.count() + test_df.count():,}")

# COMMAND ----------

print("TRAIN")
(
    train_df
    .groupBy("DEFAULT")
    .count()
    .withColumn(
        "percentage",
        F.round(F.col("count") / F.lit(train_df.count()) * 100, 2)
    )
    .orderBy("DEFAULT")
    .show()
)

print("TEST")
(
    test_df
    .groupBy("DEFAULT")
    .count()
    .withColumn(
        "percentage",
        F.round(F.col("count") / F.lit(test_df.count()) * 100, 2)
    )
    .orderBy("DEFAULT")
    .show()
)

# COMMAND ----------


preprocessing_model = preprocessing_pipeline.fit(train_df)

train_prepared = preprocessing_model.transform(train_df)
test_prepared = preprocessing_model.transform(test_df)

print(f"Train preparado: {train_prepared.count():,}")
print(f"Test preparado: {test_prepared.count():,}")

# COMMAND ----------

train_prepared.select(
    "ID",
    "DEFAULT",
    "features"
).show(5, truncate=False)

# COMMAND ----------

first_vector = train_prepared.select("features").first()["features"]

print(f"Dimensión final del vector de features: {len(first_vector)}")

# COMMAND ----------

TRAIN_TABLE = "workspace.bigdata_milagros_1.tp_final_train"
TEST_TABLE = "workspace.bigdata_milagros_1.tp_final_test"

(
    train_prepared
    .select("DEFAULT", "features")
    .write
    .mode("overwrite")
    .saveAsTable(TRAIN_TABLE)
)

(
    test_prepared
    .select("DEFAULT", "features")
    .write
    .mode("overwrite")
    .saveAsTable(TEST_TABLE)
)

print("Datasets preparados guardados correctamente.")
print(f"Train: {TRAIN_TABLE}")
print(f"Test:  {TEST_TABLE}")