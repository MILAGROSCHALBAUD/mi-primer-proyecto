# Resolución Práctica 2


Clase práctica 2 --- Silver, Gold y orquestación
Propósito
Transformar las tablas Bronze de la práctica 1 en datos confiables y
productos analíticos. El flujo se ejecuta como un Lakeflow Job, admite
archivos nuevos y demuestra idempotencia mediante validaciones
automáticas.
Objetivos
- Aplicar contratos de tipos y reglas de calidad.
- Separar registros válidos de una cuarentena explicable.
- Resolver duplicados y correcciones con MERGE.
- Construir tablas Gold.
- Orquestar notebooks dependientes con Lakeflow Jobs.
- Probar una carga nueva sin cambiar el código del pipeline.
- Verificar reconciliación e idempotencia.
Requisitos previos
La práctica 1 debe haber creado, en el mismo esquema:
bronze_customers
bronze_products
bronze_transactions
bronze_events
Usá en todos los notebooks el mismo student_id y la misma escala de la
práctica 1. Si trabajaste con small, no cambies a test: las claves
foráneas se generan de acuerdo con la escala.
Secuencia
1. Ejecutá 00_preflight.ipynb.
2. Ejecutá manualmente 00_generate_new_batch.ipynb con batch_002.
3. Creá el Job siguiendo GUIA_CREAR_JOB.md.
4. Ejecutá el Job con expected_batch_id=batch_002.
5. Revisá las cuatro tareas y las tablas resultantes.
6. Ejecutá nuevamente el mismo Job sin crear otro archivo.
7. Confirmá que la segunda validación informa métricas estables.
8. Volvé a ejecutar manualmente 00_generate_new_batch.ipynb, esta vez
   con batch_id=batch_003.
9. Ejecutá el Job con expected_batch_id=batch_003 y verificá que el
   nuevo lote aparezca en gold_batch_summary.
10. Ejecutá manualmente 05_visualizacion.ipynb y resolvé las cuatro
    preguntas usando las tablas Gold.
Qué hace expected_batch_id
El pipeline no necesita expected_batch_id para encontrar ni
procesar archivos. La tarea de ingesta usa COPY INTO sobre el
directorio de entrada, detecta automáticamente batch_003 como un
archivo nuevo y lo incorpora de manera incremental. Silver y Gold
procesan después los datos resultantes sin requerir cambios en el
código.
expected_batch_id se utiliza solamente en
04_validate_pipeline.ipynb: expresa qué lote esperamos comprobar en
esa ejecución. Al crear batch_003, cambiar el parámetro a batch_003
permite validar que ese lote llegó a Bronze, fue aceptado o enviado a
cuarentena, aparece en Gold y aplicó la corrección esperada.
Si se deposita batch_003 pero se conserva
expected_batch_id=batch_002, el ETL igualmente procesará el archivo
nuevo. Sin embargo, la tarea validate puede fallar porque seguirá
evaluando las expectativas de batch_002 y comparando la corrida como
si fuera una reejecución sin datos nuevos. El estado rojo representa
entonces una expectativa de prueba incorrecta, no una incapacidad del
pipeline para detectar el archivo.
Tablas resultantes
bronze_transactions_incremental
bronze_transactions_all       (vista)
silver_customers
silver_products
silver_transactions
silver_transactions_quarantine
gold_daily_sales
gold_customer_risk
gold_batch_summary
pipeline_run_audit
Preguntas de análisis y comprensión
Respondé las siguientes preguntas después de completar las ejecuciones
con batch_002 y batch_003. En las preguntas de análisis incluí la
consulta SQL o PySpark utilizada y el resultado relevante. En las
preguntas sobre código, indicá el notebook y la sección que fundamentan
tu respuesta.
Análisis de las tablas
1. ¿Cuántas filas físicas recibió cada lote en
   bronze_transactions_incremental? Escribí una consulta que muestre
   el resultado por source_batch_id.
2. Para cada lote, ¿cuántas transacciones fueron aceptadas y cuántas
   quedaron en silver_transactions_quarantine? Reconciliá tus
   resultados con gold_batch_summary.
3. ¿Qué motivos de rechazo aparecen en la cuarentena y cuántos
   registros tiene cada uno por lote? ¿Los rechazos observados
   coinciden con los casos introducidos por el generador?
4. Seguí la transacción 42 desde bronze_transactions_all hasta
   silver_transactions. ¿Cuántas versiones existen en Bronze y cuál
   quedó vigente en Silver? Mostrá las columnas que justifican la
   elección.
5. Comprobá mediante una consulta que silver_transactions tiene una
   sola fila por transaction_id. ¿Qué resultado indicaría que la
   deduplicación falló?
6. Calculá la tasa de rechazo de cada lote como
   rechazadas / (aceptadas + rechazadas) en gold_batch_summary. ¿Es
   correcto comparar solamente las cantidades absolutas si los lotes
   tienen tamaños diferentes?
7. ¿Qué día presenta el mayor monto total y cuál presenta la mayor
   cantidad de transacciones? Consultá gold_daily_sales y explicá si
   ambos máximos coinciden.
8. ¿Qué canal de pago tiene la mayor tasa global de fraude? Calculala
   como SUM(fraud_transactions) / SUM(transaction_count) y explicá
   por qué no corresponde promediar directamente fraud_rate.
9. ¿Qué combinación de país y categoría concentra el mayor monto
   vendido? Mostrá también la combinación líder dentro de cada país.
10. Compará las dos primeras filas de pipeline_run_audit
    correspondientes a la reejecución de batch_002. ¿Qué métricas
    permanecen iguales y qué columna demuestra que se realizó la
    comparación de idempotencia?
Interpretación del código y del pipeline
11. En 01_ingest_bronze_incremental.ipynb, ¿qué problema resuelve
    COPY INTO y qué información utiliza para evitar cargar dos veces
    el mismo archivo físico?
12. ¿Por qué la vista bronze_transactions_all usa UNION ALL en lugar
    de eliminar duplicados? ¿En qué capa se resuelven los duplicados de
    negocio y por qué?
13. ¿Por qué las transacciones iniciales reciben
    source_batch_id='initial' y usan event_ts como updated_at?
    ¿Cómo afecta eso a la corrección de la transacción 42?
14. En quality_rules.py, ¿qué ventaja ofrece try_cast frente a un
    cast convencional cuando llega un importe como N/A?
15. Las reglas de calidad asignan una única quality_reason. ¿Qué
    sucede si un registro viola más de una regla y por qué importa el
    orden de las condiciones?
16. Explicá cómo se construye _record_key y cómo se usa junto con
    row_number. ¿Qué caso cubre el hash cuando transaction_id no
    puede convertirse a un número?
17. Interpretá las dos cláusulas principales del MERGE de
    silver_transactions. ¿Cuándo se actualiza una fila existente y
    cuándo se inserta una nueva?
18. ¿Por qué las tablas Gold se reconstruyen completamente en esta
    práctica mientras Silver se actualiza con MERGE? Mencioná una
    ventaja y una limitación de cada estrategia.
19. ¿Por qué expected_batch_id no participa en la detección del
    archivo nuevo? Indicá qué parte del pipeline descubre batch_003 y
    qué parte utiliza el parámetro.
20. Si la tarea build_silver falla, ¿qué ocurre con build_gold y
    validate en el Job? Explicá cómo las dependencias del DAG evitan
    publicar o validar resultados incompletos.
Duración estimada
  Bloque                                  Minutos
  Repaso y preflight                           15
  Contratos, calidad y cuarentena              25
  Silver y MERGE                             30
  Pausa                                        10
  Gold y reconciliación                        25
  Construcción del Job                         25
  Archivo nuevo y primera ejecución            20
  Segunda ejecución y cierre                   10
  Visualización orientada a preguntas          20
Entrega
En tu repositorio personal creá resolucion-practica-2/ con:
resolucion-practica-2/
├── README.md
├── 02_build_silver.ipynb
├── 03_build_gold.ipynb
├── 04_validate_pipeline.ipynb
└── 05_visualizacion.ipynb
El README.md debe incluir:
- Nombre y student_id.
- Captura del DAG del Job con las cuatro tareas.
- URL del Job o su nombre exacto.
- Resultados de la primera y segunda ejecución.
- Cantidades aceptadas y rechazadas para batch_002.
- Explicación breve de por qué COPY INTO y MERGE resuelven
  problemas diferentes.
- Las cuatro visualizaciones y una respuesta explícita para cada
  pregunta.
- Respuestas a las 20 preguntas de análisis y comprensión, incluyendo
  las consultas utilizadas cuando corresponda.
No incluyas datos, credenciales ni tokens.
Resolución --- Práctica 2
Nombre: Milagros Chalbaud
student_id: milagros_1
Escala: small
Job: bigdata_milagros_1_silver_gold
Captura del DAG:

### DAG del Job

![DAG del Job](dag_job.png)

### Ejecuciones del Job

![Ejecuciones exitosas del Job](ejecuciones_job.png)

Resultados de ejecución
Se ejecutó el pipeline con batch_002 y luego se realizó una segunda
ejecución sin generar un archivo nuevo para comprobar la idempotencia.
La validación finalizó correctamente y la segunda corrida mantuvo las
mismas métricas que la primera, con idempotence_compared = True.
Luego se generó batch_003, se actualizó expected_batch_id a
batch_003 y se volvió a ejecutar el Job. La corrida finalizó
correctamente y el nuevo lote quedó incorporado en las tablas Silver y
Gold.
Para batch_002 se obtuvieron 200 transacciones aceptadas y 2
rechazadas, es decir, 202 registros considerados en la reconciliación
del lote.
COPY INTO y MERGE
COPY INTO y MERGE resuelven problemas distintos. COPY INTO se
utiliza en la ingesta Bronze incremental y evita volver a cargar un
mismo archivo físico en sucesivas ejecuciones. En cambio, MERGE
trabaja sobre los datos de negocio en Silver: permite actualizar una
transacción existente cuando llega una versión más reciente e insertar
aquellas transacciones que todavía no existen.
Preguntas de análisis y comprensión
Análisis de las tablas
1. ¿Cuántas filas físicas recibió cada lote en bronze_transactions_incremental?
Consulta:
SELECT source_batch_id, COUNT(*) AS filas_fisicas
FROM bronze_transactions_incremental
GROUP BY source_batch_id
ORDER BY source_batch_id;
En la ejecución realizada, batch_002 quedó asociado a 202
registros y batch_003 a 203 registros en la reconciliación del
pipeline. La consulta anterior permite verificar directamente la
cantidad física almacenada en Bronze incremental por lote.
2. Para cada lote, ¿cuántas transacciones fueron aceptadas y cuántas quedaron en cuarentena?
Consulta:
SELECT
    source_batch_id,
    accepted_transactions,
    rejected_transactions
FROM gold_batch_summary
ORDER BY source_batch_id;
Resultado:
  Lote            Aceptadas   Rechazadas
  initial          49.948           51
  batch_002           200            2
  batch_003           201            2
Los resultados coinciden con la reconciliación de gold_batch_summary,
que se construye a partir de las transacciones aceptadas en Silver y de
los registros almacenados en cuarentena.
3. ¿Qué motivos de rechazo aparecen en la cuarentena y cuántos registros tiene cada uno por lote?
Consulta:
SELECT
    source_batch_id,
    quality_reason,
    COUNT(*) AS cantidad
FROM silver_transactions_quarantine
GROUP BY source_batch_id, quality_reason
ORDER BY source_batch_id, quality_reason;
Las causas posibles están definidas por las reglas de calidad:
INVALID_TRANSACTION_ID, INVALID_CUSTOMER_ID, INVALID_PRODUCT_ID,
INVALID_EVENT_TS, INVALID_AMOUNT, INVALID_PAYMENT_CHANNEL,
INVALID_FRAUD_FLAG, INVALID_UPDATED_AT, UNKNOWN_CUSTOMER y
UNKNOWN_PRODUCT.
En los lotes generados se observaron 2 rechazos en batch_002 y 2 en
batch_003. Para documentar el motivo exacto de esos cuatro registros
sin inferirlo, el resultado de la consulta anterior es el que debe
tomarse como evidencia de la ejecución.
4. Seguí la transacción 42 desde Bronze hasta Silver.
Consultas:
SELECT
    transaction_id,
    amount,
    source_batch_id,
    updated_at
FROM bronze_transactions_all
WHERE transaction_id = '42'
ORDER BY updated_at;
SELECT
    transaction_id,
    amount,
    source_batch_id,
    updated_at
FROM silver_transactions
WHERE transaction_id = 42;
Bronze conserva las distintas versiones de la transacción porque la
vista usa UNION ALL. Silver, en cambio, conserva una única versión
vigente de cada transaction_id, seleccionando primero la versión más
reciente por updated_at y aplicando luego el MERGE. En la validación
final, la transacción 42 debe quedar con amount = 1999.99 y con
source_batch_id correspondiente al lote esperado en esa ejecución;
para la corrida final, batch_003.
5. Comprobación de unicidad de transaction_id en Silver
Consulta:
SELECT transaction_id, COUNT(*) AS cantidad
FROM silver_transactions
GROUP BY transaction_id
HAVING COUNT(*) > 1;
El resultado esperado es 0 filas. Si la consulta devolviera uno o
más transaction_id, significaría que existen claves repetidas y que la
deduplicación falló.
6. Tasa de rechazo por lote
Consulta:
SELECT
    source_batch_id,
    accepted_transactions,
    rejected_transactions,
    rejected_transactions /
      (accepted_transactions + rejected_transactions) AS rejection_rate
FROM gold_batch_summary
ORDER BY source_batch_id;
Resultados:
- initial: 51 / 49.999 = 0,10%
- batch_002: 2 / 202 = 0,99%
- batch_003: 2 / 203 = 0,99%
No es correcto comparar únicamente cantidades absolutas cuando los lotes
tienen tamaños distintos. Dos rechazos representan una proporción mucho
mayor en un lote de aproximadamente 200 registros que en uno de casi
50.000.
7. Día con mayor monto y mayor cantidad de transacciones
Consulta PySpark:
from pyspark.sql import functions as F

daily_df = spark.table(daily)

daily_totals = (
    daily_df
    .groupBy("sale_date")
    .agg(
        F.sum("total_amount").alias("total_amount"),
        F.sum("transaction_count").alias("transaction_count")
    )
)

daily_totals.orderBy(F.desc("total_amount")).show()
daily_totals.orderBy(F.desc("transaction_count")).show()
El 1 de marzo de 2026 fue el día con mayor monto vendido, con
7.310.840,77, y también el de mayor cantidad de transacciones, con
7.236 operaciones. Los máximos coinciden, por lo que el pico de
ventas está asociado principalmente a un mayor volumen de operaciones y
no necesariamente a un aumento excepcional del ticket promedio.
8. Canal con mayor tasa global de fraude
Consulta PySpark:
fraude_canal = (
    spark.table(daily)
    .groupBy("payment_channel")
    .agg(
        F.sum("fraud_transactions").alias("fraud_transactions"),
        F.sum("transaction_count").alias("transaction_count")
    )
    .withColumn(
        "fraud_rate",
        F.col("fraud_transactions") / F.col("transaction_count")
    )
    .orderBy(F.desc("fraud_rate"))
)
El canal transfer presenta la mayor tasa global de fraude, con
13,91%, sobre 16.723 transacciones, de las cuales 2.327
fueron fraudulentas. No corresponde promediar directamente fraud_rate
porque cada fila de Gold puede representar un número diferente de
transacciones; la tasa global correcta se obtiene dividiendo la suma de
fraudes por la suma de transacciones.
9. Combinación de país y categoría con mayor monto
Consulta PySpark:
pais_categoria = (
    spark.table(daily)
    .groupBy("country", "category")
    .agg(F.sum("total_amount").alias("total_amount"))
)

pais_categoria.orderBy(F.desc("total_amount")).show()
La combinación global de mayor monto es Brasil (BR) + home, con
2.361.959,97.
Líder por país:
  País   Categoría            Monto
  AR     books         2.267.722,26
  BR     home          2.361.959,97
  CL     home          2.167.748,03
  MX     books         2.235.941,63
  UY     home          2.323.924,46
No existe una categoría dominante en todos los países: home lidera en
Brasil, Chile y Uruguay, mientras que books lidera en Argentina y
México.
10. Reejecución e idempotencia de batch_002
Consulta:
SELECT *
FROM pipeline_run_audit
WHERE expected_batch_id = 'batch_002'
ORDER BY recorded_at;
En las dos ejecuciones consecutivas de batch_002 permanecieron iguales
las métricas principales: silver_rows = 50149,
quarantine_rows = 53, gold_rows = 598 y
gold_total_amount = 50286183. La columna idempotence_compared en
la segunda ejecución toma el valor True, demostrando que la corrida
fue comparada contra la anterior y que las métricas se mantuvieron
estables.
Interpretación del código y del pipeline
11. ¿Qué problema resuelve COPY INTO?
Notebook: 01_ingest_bronze_incremental.ipynb --- sección Ingesta
Bronze incremental.
COPY INTO permite realizar una ingesta incremental desde el directorio
de archivos de entrada. Databricks mantiene información sobre los
archivos físicos que ya fueron procesados, por lo que al volver a
ejecutar la tarea no vuelve a cargar el mismo CSV. De esta forma, el
pipeline puede descubrir archivos nuevos sin duplicar físicamente
archivos ya ingeridos.
12. ¿Por qué bronze_transactions_all usa UNION ALL?
Notebook: 01_ingest_bronze_incremental.ipynb --- creación de
bronze_transactions_all; 02_build_silver.ipynb --- deduplicación de
transacciones.
Se utiliza UNION ALL porque Bronze busca conservar el historial tal
como llegó, incluyendo versiones repetidas o corregidas de una misma
transacción. Los duplicados de negocio se resuelven en Silver, donde se
tipan los datos, se construye _record_key y se aplica row_number
para seleccionar la versión que debe quedar vigente.
13. ¿Por qué las transacciones iniciales usan source_batch_id='initial' y event_ts como updated_at?
Notebook: 01_ingest_bronze_incremental.ipynb --- creación de la
vista unificada.
Las transacciones originales no pertenecen a uno de los lotes
incrementales, por eso se identifican con source_batch_id='initial'.
Como no poseen un updated_at propio, se utiliza event_ts como
referencia temporal inicial. Cuando llega una corrección posterior de la
transacción 42, su updated_at es más reciente y puede reemplazar la
versión histórica durante la deduplicación y el MERGE.
14. Ventaja de try_cast frente a cast
Archivo/sección: quality_rules.ipynb --- función
add_transaction_types.
try_cast intenta convertir el dato al tipo esperado y, si el valor no
puede convertirse, devuelve NULL en lugar de interrumpir todo el
procesamiento. Por ejemplo, un amount='N/A' produce
amount_typed = NULL, lo que permite que la regla posterior lo
clasifique como INVALID_AMOUNT y lo envíe a cuarentena.
15. ¿Qué sucede si un registro viola más de una regla?
Archivo/sección: quality_rules.ipynb --- función
add_quality_reason.
Las reglas se implementan como una cadena ordenada de when, por lo que
se asigna una sola quality_reason: la primera condición que resulte
verdadera. Por eso el orden es importante; si un registro tiene
simultáneamente un transaction_id inválido y un importe inválido,
queda clasificado por la primera regla aplicable, en este caso
INVALID_TRANSACTION_ID.
16. Construcción de _record_key y uso de row_number
Notebook: 02_build_silver.ipynb --- tipado, calidad y
deduplicación.
_record_key utiliza el transaction_id tipado cuando este es válido.
Si no puede convertirse a número, se construye un hash SHA-256 a partir
de los campos raw, reemplazando los nulos por <NULL>. Luego
row_number particiona por _record_key y ordena por
updated_at_typed descendente y source_batch_id descendente; se
conserva únicamente _rn = 1.
El hash permite que los registros con transaction_id inválido también
tengan una clave determinística para deduplicación, en lugar de agrupar
todos los identificadores inválidos bajo un mismo NULL.
17. Interpretación del MERGE de silver_transactions
Notebook: 02_build_silver.ipynb --- MERGE de transacciones
válidas.
Las cláusulas principales son:
WHEN MATCHED AND s.updated_at > t.updated_at THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
Si el transaction_id ya existe, solamente se actualiza cuando la
versión entrante tiene un updated_at más reciente. Si el
transaction_id todavía no existe en Silver, se inserta como una fila
nueva. Esto permite aplicar correcciones sin duplicar la transacción de
negocio.
18. Gold reconstruido completamente vs. Silver con MERGE
Notebooks: 02_build_silver.ipynb --- Silver; 03_build_gold.ipynb
--- Gold.
Silver utiliza MERGE porque necesita mantener una representación
consolidada de las transacciones e incorporar altas y correcciones
incrementalmente. Su ventaja es evitar reconstruir toda la tabla ante
cada cambio; como limitación, requiere una lógica más cuidadosa para
decidir cuándo actualizar o insertar.
Gold se genera mediante CREATE OR REPLACE TABLE a partir del estado
actual de Silver. La ventaja es que las métricas agregadas quedan
siempre consistentes con la versión vigente de los datos; la limitación
es que reconstruir completamente las tablas puede ser más costoso a
medida que aumenta el volumen.
19. ¿Por qué expected_batch_id no detecta el archivo nuevo?
Notebooks: 01_ingest_bronze_incremental.ipynb --- ingesta;
04_validate_pipeline.ipynb --- validación.
La detección del archivo nuevo la realiza COPY INTO, que lee el
directorio incoming/transactions/ e incorpora automáticamente los
archivos físicos que todavía no fueron procesados. expected_batch_id
no controla esa ingesta: se utiliza en la validación para indicar qué
lote se espera comprobar en una determinada corrida.
Por eso batch_003 puede ser procesado aunque expected_batch_id siga
en batch_002; en ese caso, lo que puede fallar es la validación de las
expectativas, no la detección del archivo.
20. ¿Qué ocurre si falla build_silver?
Job: DAG bronze → silver → gold → validation.
build_gold depende de que build_silver termine correctamente y
validate depende de las tareas anteriores. Por lo tanto, si Silver
falla, las tareas dependientes no continúan normalmente con la
publicación y validación de resultados. Esta estructura evita construir
productos Gold o validar una corrida utilizando resultados Silver
incompletos.
Visualizaciones orientadas a preguntas
1. Evolución temporal
Pregunta: ¿Qué día tuvo el mayor monto vendido y ese día también fue
el de mayor cantidad de transacciones?
 ![Visualización 1 - Evolución diaria](visualizacion_1.png)

Respuesta: El 1 de marzo de 2026 fue el día con el mayor monto
vendido (7.310.840,77) y también registró la mayor cantidad de
transacciones (7.236). Como ambos máximos coinciden, el pico de
ventas se explica principalmente por un mayor volumen de operaciones y
no necesariamente por un aumento excepcional del ticket promedio.
2. Canal y fraude
Pregunta: ¿Qué canal de pago presenta la mayor tasa de fraude? ¿La
conclusión se sostiene al considerar el número de transacciones?

![Visualización 2 - Fraude por canal de pago](visualizacion_2.png)

Respuesta: transfer presenta la mayor tasa de fraude, con
13,91%, seguido por wallet (12,97%) y card (12,54%). Los tres
canales tienen volúmenes similares, por lo que la mayor tasa observada
en transfer no se explica por una diferencia importante en el tamaño
de los grupos.
3. Concentración geográfica y de producto
Pregunta: ¿Qué combinación de país y categoría genera el mayor
monto? ¿Existe una categoría dominante en todos los países?
![Visualización 3 - Monto vendido por país y categoría](visualizacion_3.png)

Respuesta: La combinación Brasil + home genera el mayor monto
vendido, con 2.361.959,97. No existe una única categoría dominante:
home lidera en Brasil, Chile y Uruguay, mientras que books lidera en
Argentina y México.
El gráfico de barras agrupadas es adecuado porque permite comparar
simultáneamente los países y las categorías manteniendo una escala común
para el monto.
4. Calidad del pipeline
Pregunta: ¿Qué proporción de cada lote fue aceptada y rechazada? ¿El
lote nuevo presenta una calidad diferente del lote inicial?
![Visualización 4 - Calidad por lote](visualizacion_4.png)

Respuesta: batch_002 y batch_003 presentan una aceptación del
99,01% y un rechazo del 0,99%, mientras que el lote initial
presenta 99,90% de aceptación y 0,10% de rechazo. La diferencia
debe interpretarse teniendo en cuenta el tamaño de los lotes: initial
contiene 49.999 registros, mientras que los nuevos contienen alrededor
de 200, por lo que unos pocos rechazos producen un impacto porcentual
mucho mayor.

Cierre
La práctica permitió implementar un flujo completo Bronze → Silver →
Gold con ingesta incremental, reglas de calidad, cuarentena,
deduplicación, actualización mediante MERGE, construcción de productos
analíticos y validaciones automáticas. La reejecución de batch_002
permitió comprobar la idempotencia del pipeline y la incorporación
posterior de batch_003 verificó que el flujo admite nuevos archivos
sin modificar el código del ETL.
