# Clase práctica 1 — Ingesta y capa Bronze

## Propósito

Construir la primera capa de un Lakehouse en Databricks a partir de fuentes CSV, JSON y Parquet. Al terminar, cada alumno tendrá un espacio aislado en Unity Catalog y cuatro tablas Bronze trazables.

## Duración estimada

| Bloque | Minutos |
|---|---:|
| Setup y recorrido del workspace | 25 |
| Generación de fuentes | 25 |
| Lectura, esquemas y calidad inicial | 35 |
| Pausa | 10 |
| Parquet, Delta y tablas Bronze | 40 |
| Desafío de evolución de esquema | 35 |
| Puesta en común y cierre | 10 |

## Antes de la clase

1. Completar la [guía paso a paso de Databricks Free Edition](../GUIA_SETUP_DATABRICKS_FREE.md).
2. Confirmar que se puede abrir `00_setup.ipynb` y ejecutar `SELECT current_catalog()`.
3. No instalar paquetes: la práctica usa únicamente Spark y Delta incluidos en la plataforma.

## Resultados esperados

Al finalizar deben existir:

```text
<catalogo>.bigdata_<alumno>.landing
<catalogo>.bigdata_<alumno>.bronze_customers
<catalogo>.bigdata_<alumno>.bronze_products
<catalogo>.bigdata_<alumno>.bronze_transactions
<catalogo>.bigdata_<alumno>.bronze_events
```

## Formato de entrega

La entrega se hace en el repositorio personal `mi-primer-proyecto` que creaste en la [guía de Git y GitHub](../GUIA_GIT_GITHUB.md).

### Estructura

Creá un directorio `resolucion-practica-1` en la raíz del repositorio con estos archivos:

```text
mi-primer-proyecto/
└── resolucion-practica-1/
    ├── README.md
    ├── 01_ingesta_bronze.ipynb
    └── 02_desafio.ipynb
```

| Archivo | Contenido |
|---|---|
| `README.md` | Nombre, `student_id` usado en los notebooks y respuestas de la sección **Entrega breve** de `01_ingesta_bronze`: tres observaciones sobre CSV/JSON, Parquet y Delta, y dónde aparece cada una de las cinco V. Incluí también la reflexión final del desafío (máximo 150 palabras). |
| `01_ingesta_bronze.ipynb` | Notebook ejecutado, con las salidas de las cuatro tablas Bronze y del diagnóstico de calidad. |
| `02_desafio.ipynb` | Notebook con las tres consignas resueltas y las aserciones ejecutadas sin errores. |

### Exportar los notebooks desde Databricks

1. Ejecutá cada notebook completo para que las salidas queden visibles.
2. Abrí **File → Export → IPython Notebook** y descargá el archivo `.ipynb`.
3. Copiá los archivos descargados a `resolucion-practica-1/` dentro de tu copia local del repositorio.

### Publicar la entrega

Desde la carpeta de tu repositorio:

```bash
git add resolucion-practica-1
git commit -m "Entrega práctica 1"
git push origin main
```

Verificá en GitHub que el directorio y los tres archivos aparecen en `main`.

El repositorio tiene que ser **público** para que el docente pueda ver la entrega. Para comprobarlo, abrí su URL en una ventana privada del navegador, sin iniciar sesión: si ves `resolucion-practica-1`, está accesible. Si lo creaste como privado, cambialo desde **Settings → General → Danger Zone → Change repository visibility**.

Enviá la URL de tu repositorio al mail de los profesores.

### Qué no incluir

El repositorio es público: cualquier persona puede ver los archivos y su historial. Revisá [qué implica que sea público](../GUIA_GIT_GITHUB.md#qué-implica-que-el-repositorio-sea-público) antes de hacer el push.

- Datos generados, archivos del volumen ni exportaciones de tablas: se reconstruyen ejecutando los notebooks.
- Tokens, contraseñas u otras credenciales.



Nombre = Milagros Chalbaud
student_id = milagros_1
RESPUESTAS 01_ingesta_bronze

## 1. Leer no es todavía transformar

Inspeccioná los cuatro orígenes. Compará el esquema inferido del CSV con el esquema físico de Parquet. ¿Por qué `amount` termina como texto?

Cuando uno usa un csv, tiene que especificarle el eschema (inferSchema=True) ya que Spark interpreta inicialmente los campos como string/texto. En cambio, Parquet guarda el esquema y los tipos de datos dentro del propio formato, no jhace falta eszpecificarle nada.


### Experimento: inferencia de tipos

Volvé a leer transacciones con `inferSchema=true`. Registrá cuánto tarda y verificá si resuelve correctamente `amount`. Explicá por qué inferir implica trabajo adicional y puede producir decisiones inestables.

Primero tardo 1s 5ms

Segundo no se soluciono el porblema del string esto se puede deber al echo de que amounbt no tenga un solo tipo numerico (entero,decimal) y genera que por mas que uno haga la inferencia la misma no lo tome y siga funcionando como string.


## 3. Diagnóstico inicial de calidad


Se encontraron 50.011 registros y 50.000 identificadores distintos, por lo que existen registros duplicados. Además, se detectaron 52 valores de amount que no pueden convertirse correctamente a número.


## 4. Delta y el plan de ejecución

Ejecutá `DESCRIBE DETAIL`, `DESCRIBE HISTORY` y `EXPLAIN FORMATTED` sobre una tabla. Identificá qué información agrega Delta respecto de un directorio Parquet.

Parquet: conserva información de esquema y tipos de datos. Al leer products, Spark reconoció directamente tipos como product_id: long y price: decimal(12,2), a diferencia del CSV.

Delta: además de almacenar los datos, incorpora metadatos y un historial de versiones. DESCRIBE DETAIL permitió observar información de la tabla y DESCRIBE HISTORY mostró la versión 0 y la operación con la que fue creada. Esto agrega trazabilidad respecto de trabajar solamente con archivos Parquet.


## Entrega breve

CSV/JSON: son formatos flexibles, pero la lectura puede requerir interpretar o inferir los tipos. En el caso de transacciones, amount fue leído como string y continuó siendo string incluso utilizando inferSchema=true, cuya lectura tardó aproximadamente 1,5 segundos. Esto muestra que la inferencia agrega trabajo y no garantiza identificar correctamente los tipos cuando existen valores inconsistentes.


Las cinco V aparecen en la práctica de la siguiente manera:

- Volumen: se trabaja con varias fuentes y una cantidad considerable de registros que luego se almacenan en las tablas Bronze.
- Velocidad: aparece en el tiempo necesario para leer y procesar los datos, por ejemplo al comparar la lectura normal con la inferencia de esquema.
- Variedad: los datos provienen de distintos formatos, como CSV, JSON y Parquet, y tienen diferentes estructuras.
- Veracidad: se observa al analizar la calidad de los datos. En transactions se encontraron 50.011 filas, 50.000 identificadores distintos y 52 valores de amount que no podían convertirse correctamente a número.
- Valor: los datos se organizan en una capa Bronze trazable que permite conservar la información original y prepararla para posteriores transformaciones y análisis.




02_desafio

## Reflexión final

En no más de 150 palabras, explicá la diferencia entre: detectar una evolución de esquema, aceptarla técnicamente y decidir que es válida para el negocio.


Detectar una evolución de esquema significa identificar que la estructura de los datos cambió, por ejemplo, porque apareció una nueva columna como app_version. Aceptarla técnicamente implica adaptar el proceso para poder incorporar ese cambio sin perder información previa ni romper la ingesta, manteniendo compatibilidad con los datos históricos. En este caso, se agregó la nueva columna y se utilizó NULL para los registros anteriores. Sin embargo, que un cambio pueda incorporarse técnicamente no significa que sea correcto para el negocio. Validarlo desde el negocio requiere entender qué representa el nuevo campo o valor, como refund, y confirmar que tenga sentido dentro del proceso y pueda utilizarse correctamente. Por eso, la evolución del esquema primero se detecta y se controla técnicamente, pero también necesita una validación de su significado.

