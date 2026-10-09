## Credenciales 

student_id = milagros_1

scale = small

## Preguntas

Las preguntas son cortas: buscan comprobar que entendiste la idea de cada modelo y sus ventajas y desventajas. Cuando piden un dato, copiá el número que te dio el notebook (puede variar un poco según tu escala). Alcanza con una a tres oraciones por respuesta.

### CAP y PACELC (`01_cap_pacelc`)

1. Con la red partida, ¿qué respondió la réplica `C` en modo CP y qué respondió en modo AP? ¿Qué propiedad de CAP sacrifica cada modo?
2. En modo AP, ¿qué saldo quedó en las tres réplicas después de la reparación y qué escritura se perdió?
3. Según el gráfico de latencia, ¿cuál es la p99 con `W=1` y con `W=3`? ¿Qué se gana a cambio de esperar más réplicas? (PACELC)
4. Con cinco réplicas partidas en `ABC | DE`, ¿qué lado pudo seguir escribiendo en modo CP y por qué?

### Clave-valor (`02_clave_valor`)

5. ¿Cuántas veces más rápido fue el GET en memoria que el GET con Spark? ¿Por qué Redis guarda los datos en memoria?
6. ¿Por qué para contar los clientes de AR hubo que leer y parsear todos los valores? Mencioná una ventaja y una desventaja del modelo clave-valor.
7. Al pasar de 4 a 5 nodos, ¿qué porcentaje de claves se movió con `hash mod N` y con hashing consistente? ¿Por qué conviene el segundo?

### Documental (`03_documental`)

8. ¿Cuántas filas devolvió la consulta relacional del cliente 42 y cuántos documentos la documental? ¿Qué datos quedaron embebidos dentro del documento?
9. Al leer documentos con campos distintos, ¿qué hizo Spark con los campos que faltaban en algunos? ¿Por qué se dice que el modelo documental tiene esquema flexible?
10. ¿Cuánto pesa el documento más grande? ¿Qué problema aparece si un documento crece sin límite?
11. Para calcular el monto por categoría hubo que usar `explode`. ¿Qué tipo de consultas resuelve bien el modelo documental y cuáles le cuestan más?

### Grafos (`04_grafos`)

12. ¿Cuántos nodos `Customer`, nodos `Device` y aristas `USES` tiene el grafo?
13. ¿Cuántos joins necesitó SQL para el patrón de 2 saltos y para el de 4? ¿Por qué Neo4j recorre relaciones más eficientemente que una base relacional?
14. ¿Cuántas iteraciones tardó en converger la búsqueda de componentes conexos y cuántos nodos tiene el componente más grande?
15. ¿Qué porcentaje de aristas quedó entre máquinas distintas al repartir los nodos con `hash(id) mod 4`? ¿Por qué es difícil distribuir una base de grafos?

### Vectorial (`05_vectorial`)

16. ¿Qué representa el vector de cada cliente y qué mide la similitud coseno?
17. ¿Qué porcentaje de clientes marcados hay entre los vecinos de clientes marcados y cuál es la tasa base? ¿Para qué sirve buscar "vecinos parecidos"?
18. En la curva del índice IVF, ¿qué recall y qué porcentaje de vectores escaneados se obtienen con `nprobe=4`? ¿Qué se gana y qué se pierde con la búsqueda aproximada (ANN)?

### Columnar (`06_columnar`)

19. ¿Cuánto ocupan los datos en CSV, JSON y Parquet? ¿Qué columnas leyó Spark para la consulta de `amount` sobre Parquet (`ReadSchema`)? ¿Cuántos archivos se pueden saltear con los datos ordenados?
20. ¿Por qué el formato columnar es bueno para analítica y poco conveniente para modificar una fila por vez?



## RESPUESTAS

## CAP y PACELC (`01_cap_pacelc`)

1.Con la red partida, en modo **CP** la réplica C respondió `ERROR: no disponible`, porque quedó sin quórum; este modo sacrifica disponibilidad para mantener consistencia. En modo **AP**, C respondió con el saldo viejo `100`, sacrificando consistencia para mantener disponibilidad.

2.Después de reparar la red en modo AP, las tres réplicas quedaron con saldo `50`. Se perdió la escritura `saldo=80` realizada en A/B, porque la escritura `saldo=50` en C tenía una versión más nueva y ganó mediante *last-write-wins*.

3.La p99 fue aproximadamente **9.6 ms con W=1** y **55.6 ms con W=3**. Al esperar más réplicas aumenta la latencia, pero se gana mayor consistencia y durabilidad de la escritura, mostrando el trade-off de PACELC.

4.Con cinco réplicas divididas en `ABC | DE`, el lado **ABC** pudo seguir escribiendo en modo CP porque conserva una mayoría de 3 de las 5 réplicas, es decir, tiene quórum.

## Clave-valor (`02_clave_valor`)

5.El GET en memoria fue aproximadamente **2,262,664 veces más rápido** que el GET con Spark. Redis mantiene los datos en memoria para acceder a ellos con muy baja latencia, evitando el costo de realizar consultas analíticas y accesos a almacenamiento.

6.Para contar los clientes de AR hubo que leer y parsear los **5,000 valores**, porque `country` estaba almacenado dentro del valor y no como un campo directamente consultable. Una ventaja del modelo clave-valor es la rapidez para buscar por clave; una desventaja es que las consultas por atributos internos del valor son costosas.

7.Al pasar de 4 a 5 nodos se movió aproximadamente **79.6% de las claves con `hash mod N`** y **21.2% con hashing consistente**. El hashing consistente conviene porque al agregar o quitar un nodo sólo necesita redistribuir una parte de las claves.

## Documental (`03_documental`)

8.La consulta relacional del cliente 42 devolvió **11 filas**, mientras que la documental devolvió **1 documento**. Dentro del documento quedaron embebidos el perfil, las estadísticas y las transacciones del cliente, incluyendo los datos del producto de cada transacción.

9.Spark representó con `null` los campos que no estaban presentes en algunos documentos. El modelo documental tiene esquema flexible porque distintos documentos de una misma colección pueden tener campos o estructuras diferentes.

10.El documento más grande pesa aproximadamente **5.2 KB**. Si un documento crece sin límite puede volverse costoso de leer, transferir y actualizar, además de poder alcanzar el límite máximo de tamaño permitido por la base.

11.El modelo documental funciona bien para consultas que recuperan una entidad completa junto con sus datos relacionados, especialmente cuando están embebidos en el mismo documento. Le cuestan más las consultas analíticas y agregaciones sobre arrays internos, ya que es necesario desanidar estructuras, por ejemplo mediante `explode`.

## Grafos (`04_grafos`)

12.El grafo tiene **5,000 nodos Customer**, **2,361 nodos Device** y **5,400 aristas USES**.

13.SQL necesitó **3 joins para el patrón de 2 saltos** y **5 joins para el de 4 saltos**. Neo4j puede recorrer relaciones de forma más eficiente porque las conexiones entre nodos están representadas explícitamente, evitando realizar una sucesión de joins para cada salto.

14.La búsqueda de componentes conexos tardó **14 iteraciones** en converger. El componente más grande tiene **23 nodos**.

15.Con `hash(id) mod 4`, aproximadamente **74.4% de las aristas** quedaron entre máquinas distintas. Distribuir grafos es difícil porque los nodos están muy relacionados entre sí y una partición puede generar muchas relaciones que crucen máquinas, aumentando la comunicación por red.

## Vectorial (`05_vectorial`)

16.El vector de cada cliente representa sus características de comportamiento en un espacio de **10 dimensiones**. La similitud coseno mide qué tan parecida es la dirección de dos vectores, permitiendo identificar clientes con perfiles similares.

17.Entre los vecinos de clientes marcados, **31.6% estaban marcados**, frente a una tasa base de **14.8%**. Buscar vecinos parecidos permite encontrar clientes con comportamientos similares y puede servir, por ejemplo, para detectar casos potencialmente relacionados con fraude.

18.Con `nprobe=4`, el índice IVF obtuvo un **recall@10 de 0.872 (87.2%)** escaneando aproximadamente **5.985% de los vectores**. La búsqueda aproximada (ANN) reduce mucho la cantidad de vectores que hay que comparar y mejora la velocidad, a cambio de poder perder algunos de los vecinos verdaderamente más cercanos.

## Columnar (`06_columnar`)

19.Los datos ocuparon aproximadamente **50.0 MB en CSV, 121.1 MB en JSON y 5.3 MB en Parquet**. Para la consulta sobre `amount`, Spark leyó solamente `ReadSchema: struct<amount:decimal(12,2)>`. Con los datos ordenados por `amount` se pudieron saltear **7 de 8 archivos**, mientras que con los datos distribuidos al azar no se pudo saltear ninguno.

20.El formato columnar es bueno para analítica porque permite leer sólo las columnas necesarias, comprime eficientemente y puede aprovechar estadísticas para saltear bloques de datos. En cambio, es poco conveniente para modificar una fila por vez porque los datos están organizados por columnas y las actualizaciones puntuales resultan más costosas.
