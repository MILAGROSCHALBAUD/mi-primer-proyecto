# Trabajo Práctico Final — Big Data

**Alumna:** Milagros Chalbaud  
**Variante:** 2 — Ejecución  
**Opción:** B — Experimentación y comparación de modelos con MLflow

## Objetivo

El objetivo del trabajo es desarrollar y comparar distintos modelos de clasificación para predecir el incumplimiento de pago de clientes de tarjetas de crédito.

Se utiliza Apache Spark para el procesamiento y entrenamiento de los modelos y MLflow para registrar parámetros, métricas y artifacts de los experimentos.

## Dataset

Se utiliza el dataset **Default of Credit Card Clients**, publicado en UCI Machine Learning Repository.

El dataset contiene información de 30.000 clientes de tarjetas de crédito de Taiwán.

La variable objetivo es `DEFAULT`:

- `0`: cliente sin default.
- `1`: cliente con default.

El dataset presenta un desbalance moderado de clases, con aproximadamente 22% de observaciones pertenecientes a la clase positiva.

Fuente:

UCI Machine Learning Repository — Default of Credit Card Clients  
https://archive.ics.uci.edu/dataset/350/default%2Bof%2Bcredit%2Bcard%2Bclients

## Estructura del trabajo

El desarrollo se encuentra en la carpeta `Notebooks/`.

### 01-EDA

Análisis exploratorio del dataset:

- carga y corrección de la estructura original;
- análisis de tipos de datos;
- control de valores nulos y duplicados;
- distribución de la variable objetivo;
- análisis descriptivo de variables relevantes;
- análisis de la relación entre distintas variables y `DEFAULT`.

### 02-PREPROCESSING

Preparación de los datos para modelado:

- recodificación de categorías residuales;
- tratamiento de variables categóricas mediante `StringIndexer` y `OneHotEncoder`;
- construcción del vector de features mediante `VectorAssembler`;
- partición reproducible entre entrenamiento y test;
- almacenamiento de los conjuntos preparados en tablas de Unity Catalog.

La partición oficial utilizada contiene:

- Train: 24.001 observaciones.
- Test: 5.999 observaciones.

### 03-MLFLOW-MODELS

Entrenamiento y comparación inicial de tres algoritmos:

- Logistic Regression;
- Random Forest;
- Gradient-Boosted Trees (GBT).

Para cada modelo se registran experimentos mediante MLflow y se analizan métricas globales y métricas específicas de la clase positiva.

GBT presentó el mejor desempeño general y fue seleccionado para una etapa adicional de ajuste.

### 04-MODEL-COMPARISON

Se comparan distintas configuraciones de Gradient-Boosted Trees.

El conjunto de entrenamiento se divide internamente en:

- Fit: 19.112 observaciones.
- Validation: 4.889 observaciones.

Los hiperparámetros se seleccionan utilizando exclusivamente el conjunto de validación, manteniendo el conjunto de test reservado para la evaluación final.

El modelo seleccionado fue:

- `maxDepth = 3`
- `maxIter = 50`
- `stepSize = 0.1`

La selección se realizó principalmente mediante **PR-AUC**.

Posteriormente se evaluaron distintos thresholds de clasificación sobre validation. El threshold seleccionado fue **0.30**, maximizando el F1 de la clase positiva.

Finalmente, el modelo seleccionado fue reentrenado utilizando las 24.001 observaciones del conjunto de entrenamiento y evaluado una única vez sobre las 5.999 observaciones del conjunto de test.

## Resultados finales

Resultados obtenidos sobre el conjunto de test:

| Métrica | Resultado |
|---|---:|
| ROC-AUC | 0.7884 |
| PR-AUC | 0.5573 |
| Accuracy | 0.8043 |
| Precision — DEFAULT=1 | 0.5566 |
| Recall — DEFAULT=1 | 0.5202 |
| F1 — DEFAULT=1 | 0.5378 |

Matriz de confusión:

| | Predicción 0 | Predicción 1 |
|---|---:|---:|
| Real 0 | 4142 | 544 |
| Real 1 | 630 | 683 |

## MLflow

MLflow se utiliza para registrar los experimentos realizados durante el trabajo.

Se registran:

- hiperparámetros de los modelos;
- ROC-AUC;
- PR-AUC;
- accuracy;
- precision, recall y F1 de la clase positiva;
- matriz de confusión;
- comparación de thresholds;
- artifacts asociados a la evaluación.

Esto permite mantener trazabilidad entre las distintas configuraciones evaluadas y la configuración finalmente seleccionada.

## Reproducción

Los notebooks deben ejecutarse en el siguiente orden:

1. `01-EDA`
2. `02-PREPROCESSING`
3. `03-MLFLOW-MODELS`
4. `04-MODEL-COMPARISON`

El dataset debe estar disponible en el entorno de Databricks antes de ejecutar el primer notebook.

Los notebooks utilizan PySpark, Spark MLlib y MLflow.

## Criterio de evaluación

Debido al desbalance de la variable objetivo, la comparación no se basa únicamente en accuracy.

Se consideran ROC-AUC y especialmente PR-AUC, además de precision, recall y F1 de la clase positiva (`DEFAULT=1`).

La selección del threshold se realiza sobre el conjunto de validación y no sobre test, evitando utilizar el conjunto de evaluación final durante la selección del modelo.

## Limitaciones

El análisis utiliza un único dataset y un conjunto acotado de modelos y configuraciones.

Como extensiones futuras podrían evaluarse:

- una búsqueda más amplia de hiperparámetros;
- validación cruzada;
- otros algoritmos de clasificación;
- técnicas adicionales para el tratamiento del desbalance;
- análisis de interpretabilidad de las variables.

## Referencias

UCI Machine Learning Repository.  
Default of Credit Card Clients.