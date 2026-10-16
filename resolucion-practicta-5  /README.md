
Nombre: Milagros Chalbaud

student_id: milagros_1

Escala: small

Tabla de runs

  run          modelo                features    class_weight   umbral   hiperparametros        train_pr_auc   pr_auc   accuracy   precision   recall   f1
  
  82           gradient_boosting     completas   ninguno        0.5      learning_rate=0.1,     0.674          0.585    0.918      0.700       0.372    0.485
                                                                         max_depth=sin_limite                                                           
  
  5            logistic_regression   completas   balanced       0.3      C=0.1                  0.527          0.540    0.617      0.202       0.909    0.330
  
  umbral=0.2   random_forest         completas   ninguno        0.2      n_estimators=100,      1.000          0.537    0.850      0.381       0.705    0.495
                                                                         max_depth=sin_limite                                                           
  
  umbral=0.3   random_forest         completas   ninguno        0.3      n_estimators=100,      1.000          0.537    0.894      0.490       0.580    0.531
                                                                         max_depth=sin_limite                                                           
  
  umbral=0.4   random_forest         completas   ninguno        0.4      n_estimators=100,      1.000          0.537    0.912      0.602       0.464    0.524
                                                                         max_depth=sin_limite                                                           
  
  umbral=0.5   random_forest         completas   ninguno        0.5      n_estimators=100,      1.000          0.537    0.916      0.689       0.341    0.456
                                                                         max_depth=sin_limite                                                           
  
  umbral=0.2   random_forest         completas   ninguno        0.2      n_estimators=100,      1.000          0.537    0.850      0.381       0.705    0.495
                                                                         max_depth=sin_limite                                                           
  
  umbral=0.3   random_forest         completas   ninguno        0.3      n_estimators=100,      1.000          0.537    0.894      0.490       0.580    0.531
                                                                         max_depth=sin_limite                                                           
  
  umbral=0.4   random_forest         completas   ninguno        0.4      n_estimators=100,      1.000          0.537    0.912      0.602       0.464    0.524
                                                                         max_depth=sin_limite                                                           
  
  umbral=0.5   random_forest         completas   ninguno        0.5      n_estimators=100,      1.000          0.537    0.916      0.689       0.341    0.456
                                                                         max_depth=sin_limite                                                           
  
  umbral=0.2   random_forest         completas   ninguno        0.2      n_estimators=100,      1.000          0.537    0.850      0.381       0.705    0.495
                                                                         max_depth=sin_limite                                                           
  
  umbral=0.3   random_forest         completas   ninguno        0.3      n_estimators=100,      1.000          0.537    0.894      0.490       0.580    0.531
                                                                         max_depth=sin_limite                                                           
  
  umbral=0.4   random_forest         completas   ninguno        0.4      n_estimators=100,      1.000          0.537    0.912      0.602       0.464    0.524
                                                                         max_depth=sin_limite                                                           
  
  umbral=0.5   random_forest         completas   ninguno        0.5      n_estimators=100,      1.000          0.537    0.916      0.689       0.341    0.456
                                                                         max_depth=sin_limite                                                           
  
  83           random_forest         completas   ninguno        0.5      n_estimators=100,      1.000          0.537    0.916      0.689       0.341    0.456
                                                                     max_depth=sin_limite                                                           

Respuestas

1. Splits y porcentaje de contracargos

train tiene 35.654 filas y 11,05% de contracargos; test
tiene 7.129 filas y 10,38%; nuevas tiene 7.165 filas y
11,05%. La separación es temporal para simular el uso real: se
entrena con el pasado y se evalúa sobre transacciones posteriores,
evitando mezclar información futura en el entrenamiento.


2. Baseline y PR-AUC

Un modelo que siempre predice "sin contracargo" obtiene 89,6% de
accuracy, aun sin detectar ningún contracargo. Por eso se usa PR-AUC:
con clases desbalanceadas evalúa mejor la capacidad del modelo para
identificar y ordenar los casos positivos.


3. Run manual y diferencia entre experimento y run

En 01_manual_logistica se registraron parámetros como C=1.0,
feature_set=basicas, model_type=logistic_regression,
class_weight=ninguno y threshold=0.5; métricas como PR-AUC, ROC-AUC,
accuracy, precision, recall y F1; y el artefacto matriz_confusion.png.
Un experimento agrupa múltiples ejecuciones comparables, mientras que un
run representa una ejecución concreta con su configuración y resultados.


4. Autolog

Autolog registró 46 parámetros y métricas de entrenamiento como
accuracy, F1, log loss, precision, recall y ROC-AUC. Además generó
artefactos automáticamente, pero el registro manual permitió agregar
información específica del problema, como las métricas de test, el
umbral, el conjunto de features y la cantidad de alertas.


5. Reproducibilidad

Sí, 01_repro_a y 01_repro_b dieron métricas idénticas. Para que un
run sea reproducible hay que fijar los datos/versionado, el código, la
semilla aleatoria y el entorno/dependencias.


6. Firma del modelo

Al llamar al modelo sin la columna amount se produjo un error de
validación de esquema, porque la firma exige amount y
payment_channel. La signature documenta y valida las entradas y
salidas esperadas del modelo, evitando inferencias con datos
incompatibles.


7. Mejor run

El mejor fue el run 82, con gradient_boosting, features
completas, learning_rate=0.1, max_depth=sin_limite, sin
class_weight y umbral 0.5. Obtuvo PR-AUC = 0.585, frente a
0.170 usando sólo rule_alert, una mejora absoluta de 0.415.


8. Conjuntos de variables e importancia

En los runs comparables disponibles, el random_forest pasó de PR-AUC
0.510 con cliente a 0.537 con completas; no quedó registrada
una corrida basicas del mismo random forest para completar una
comparación estrictamente idéntica entre los tres conjuntos. En el mejor
run, las variables más importantes fueron amount (0.3293),
payment_channel (0.1834), hour (0.1509), category (0.0815) y
account_age_days (0.0599).


9. Comparación de modelos

Con features completas, el mejor resultado fue Gradient Boosting
(0.585), por encima de logística (0.540) y Random Forest (0.537). Los
árboles pueden representar interacciones y relaciones no lineales, por
ejemplo que una operación sea simultáneamente nocturna y por
transferencia, sin tener que crear explícitamente esa interacción como
en una logística.


10. class_weight = balanced

En la comparación de Random Forest con features cliente, al usar
balanced la precision pasó aproximadamente de 0.412 a 0.418, el
recall de 0.499 a 0.465 y el PR-AUC de 0.433 a 0.421; por lo
tanto, en esta ejecución no produjo una mejora importante. La cantidad
de alertas también disminuyó, coherentemente con la caída del recall.


11. Cambio de umbral

Con Random Forest + completas, al bajar el umbral de 0.5 a 0.2, el
recall subió de 0.341 a 0.705 y las alertas aumentaron de 366 a
1.371, mientras la precision bajó de 0.689 a 0.381. El PR-AUC
permaneció en 0.537 porque se calcula sobre el ranking de scores
para todos los umbrales; F1 sí depende del punto de corte elegido.


12. Barrido y sobreajuste

En mi ejecución, el barrido que quedó registrado fue del umbral
(0.5, 0.4, 0.3, 0.2) y no de un hiperparámetro del modelo; por
eso el PR-AUC fue 0.537 en todos los casos. El Random Forest mostró
train_pr_auc = 1.000 frente a test_pr_auc = 0.537, una brecha clara
de sobreajuste (overfitting).


13. Mejor PR-AUC vs. mejor accuracy

Sí, en la ejecución final coincidieron: el run 82 fue tanto el mejor
por PR-AUC (0.585) como por accuracy (0.918). No tienen por qué
coincidir, porque en un problema desbalanceado la accuracy puede
favorecer modelos que casi siempre predicen la clase mayoritaria.


14. Train vs. test

Los Random Forest sin límite de profundidad son los que quedan más lejos
de la diagonal: tienen PR-AUC de train = 1.000 y alrededor de
0.537 en test. Esto indica sobreajuste: el modelo aprende demasiado
bien los datos de entrenamiento pero generaliza peor.


15. mlflow.search_runs

mlflow.search_runs permite consultar, filtrar, ordenar y automatizar
la comparación de muchos runs sin revisarlos manualmente en la interfaz.
Un filtro para traer Random Forest con PR-AUC de test mayor a 0.55
sería:
filter_string="params.model_type = 'random_forest' AND metrics.test_pr_auc > 0.55"


16. Costo de errores y umbral

En fraude, normalmente un contracargo no detectado implica una pérdida
económica directa, mientras que una falsa alerta agrega costo operativo
y fricción al cliente. Si riesgo sólo puede revisar una cantidad fija de
casos por día, ajustaría el umbral para que la cantidad de alertas se
acerque a esa capacidad, priorizando los scores más altos.


17. Registro en Unity Catalog

Sí. El modelo se registró como
workspace.bigdata_milagros_1.fraud_model, versión 2, con alias
champion. Usar
models:/workspace.bigdata_milagros_1.fraud_model@champion desacopla el
código consumidor de un run específico: se puede cambiar la versión
productiva moviendo el alias sin modificar el código de inferencia.


18. Inferencia y auditoría

Se puntuaron 7.165 transacciones nuevas y 383 generaron alerta
(5,3%). ml_predictions guarda transaction_id, score, alerta,
threshold, model_name, model_version, run_id y scored_at, lo
que permite auditar cada decisión. El umbral se guarda fuera del modelo
porque es una decisión operativa/de negocio que puede modificarse sin
reentrenar.


19. Monitoreo y drift

El PR-AUC en nuevas fue 0.559, cercano al 0.585 observado en
test. En la campaña simulada, el porcentaje de alertas aumentó de 5,3%
a 13,3%; esto muestra drift, es decir, un cambio en la distribución de
los datos o scores, que puede detectarse monitoreando inputs y
predicciones incluso antes de recibir las etiquetas reales.


20. Ciclo de vida MLOps

La práctica recorrió preparación/versionado de datos, entrenamiento,
tracking de experimentos, comparación, registro del champion, inferencia
batch y monitoreo. Para producción real faltarían, entre otras cosas,
automatizar el pipeline y el reentrenamiento, implementar
monitoreo y alertas continuas, validaciones de calidad de datos,
control de acceso y un mecanismo formal de despliegue/rollback.
