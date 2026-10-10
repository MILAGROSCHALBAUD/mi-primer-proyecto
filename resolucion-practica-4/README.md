# Entrega práctica 4 — Streaming

- **Nombre:** Milagros Chalbaud
- **student_id:** milagros_1
- **Escala:** small

Respondé cada pregunta en una a tres oraciones. Cuando se pide un dato, copiá el valor que te dio el notebook.

## Log y offsets

**1.** En la cola quedaron 2 mensajes y luego en el log 5 mensajes 

Cola → leídos ['pago_1', 'pago_2', 'pago_3']; quedan en la cola: ['pago_4', 'pago_5']

Log  → leídos ['pago_1', 'pago_2', 'pago_3']; el log sigue teniendo 5 mensajes; offset del consumidor = 3

**2.** 
Despues de la llegada 2 antifraude ya habia leido 180 mensajes , pero reportes hbaia leido 0. Sin embargo luego de la llegada 3 de atifraude, reportes se puso al dia y leyo todos los mensajes que venian acumulando de antuifraude 220 (se puso al dia). Como se puede ver el atraso que tiene reportes no afecta a antifraudeya porque cada consumidor tiene su propio checkpoint/offset
Resultado codigo:

llegada 1: antifraude leyó 60 mensajes nuevos; reportes leyó 0

llegada 2: antifraude leyó 120 mensajes nuevos; reportes leyó 0

llegada 3: antifraude leyó 40 mensajes nuevos; reportes leyó 220

llegada 4: antifraude leyó 40 mensajes nuevos; reportes leyó 0

llegada 5: antifraude leyó 20 mensajes nuevos; reportes leyó 60

**3.**
Se denomina OFFSET hasta qué posición del log llegó un consumidor y, por lo tanto, desde dónde debe continuar leyendo.

**4.** 
El replay leyo 280 mensajes, es decir, todo el contenido del topic. La arquitectura Kappa propone reprocesar los datos leyendo nuevamente el log desde el principio con la lógica de streaming, mientras que Lambda mantiene una capa batch y otra de streaming, duplicando la lógica de procesamiento.

## Ingesta y enriquecimiento

**5.**
Bronze procesó 60, 120, 40, 40 y 20 filas nuevas en las cinco llegadas, respectivamente. Al reejecutar sin archivos nuevos procesó 0 filas; Auto Loader, mediante su checkpoint, recuerda qué archivos ya fueron leídos y evita procesarlos nuevamente

**6.**
En la cuarentena aparecieron los motivos INVALID_AMOUNT y UNKNOWN_CUSTOMER, ambos en stream_002, con 20 registros de cada tipo. Bronze conserva el texto original para no perder información y permitir reprocesar los datos si luego cambia el contrato, la validación o la lógica de transformación.

**7.**
El enriquecimiento agregó country, proveniente de silver_customers, y category, proveniente de silver_products. Es un join stream-tabla, porque los eventos llegan como stream y se enriquecen utilizando tablas estáticas de referencia.

## Tiempo y ventanas

**8.**
El event time indica cuándo ocurrió realmente el evento, mientras que el processing time indica cuándo fue procesado por el sistema. Por ejemplo, late_ok ocurrió a las 12:03, pero llegó posteriormente; como todavía estaba dentro del margen permitido por el watermark, fue aceptado.

**9.**
Los watermarks al terminar las cinco llegadas fueron 11:54, 11:58, 12:16, 12:17 y 12:35, respectivamente. Se calculan como el máximo event time observado menos 10 minutos.

**10.**
Las primeras ventanas tumbling en modo append aparecieron en la llegada 3. Antes no se emitían porque el watermark todavía no había superado el final de ninguna ventana; en la llegada 3 avanzó hasta 12:16 y permitió cerrar las ventanas anteriores.

**11.**
late_bad, cuyo event time era 12:02, llegó en la llegada 4 cuando el watermark ya estaba en 12:16, por lo que fue descartado. late_ok, en cambio, llegó antes de que el watermark cerrara su ventana y por eso pudo incorporarse al resultado.

**12.**
Las ventanas tumbling son intervalos fijos que no se superponen, por ejemplo ventas cada 5 minutos. Las hopping se superponen, por ejemplo ventas de los últimos 10 minutos calculadas cada 5 minutos; las session agrupan actividad hasta que existe un período de inactividad, por ejemplo una sesión de navegación de un cliente que termina tras 5 minutos sin actividad.

**13.**
Para la ventana [12:00, 12:05) del canal card, en modo update se emitió dos veces: en la llegada 1 con 40 compras y monto 6000, y en la llegada 2 con 60 compras y monto 8400. En append se emitió una sola vez, en la llegada 3, con el resultado final de 60 compras y monto 8400; update entrega resultados antes pero puede corregirlos varias veces, mientras que append entrega un resultado final único pero con mayor latencia.

**14.**
Con un watermark de 1 minuto las ventanas podrían cerrarse antes, reduciendo la latencia y el estado que debe mantener el sistema. A cambio, habría menor tolerancia a eventos tardíos y se podrían descartar más datos válidos que llegan con retraso.

## Garantías y fallas

**15.**
Sin deduplicar quedaron 220 filas en el destino, mientras que deduplicando por event_id quedaron 200 filas. El productor puede enviar el mismo evento más de una vez porque, ante una falla o falta de confirmación, puede reintentar el envío para evitar perderlo.

**16.**
Al reiniciar con el mismo checkpoint el destino permaneció en 200 filas, porque Spark sabía hasta dónde había procesado. Al perder el checkpoint y volver a ejecutar con append, el destino pasó a 400 filas, mostrando un comportamiento at-least-once, ya que los eventos pueden procesarse nuevamente y generar duplicados.

**17.**
Con MERGE el destino quedó en 200 filas tanto en la primera ejecución como después de perder el checkpoint. Una escritura idempotente significa que aplicar la misma operación varias veces produce el mismo resultado que aplicarla una sola vez; en este caso, MERGE identifica cada evento por event_id y no vuelve a insertarlo.

## CDC

**18.**
CODIGO:
Eventos de cambio leídos: 13

Un UPDATE genera dos eventos porque CDC registra el estado anterior del registro y el nuevo estado, permitiendo conocer exactamente qué cambió.

**19.**
codigo: 
¿La tabla reconstruida desde el log es igual a la original? Sí

El log de CDC conserva el historial de cambios y permite conocer operaciones y estados anteriores, mientras que la tabla actual muestra únicamente el estado final de cada registro.

## Cierre

**20.**
Elegiría Spark Structured Streaming cuando ya trabajo con Spark y necesito integrar procesamiento batch y streaming a gran escala; su ventaja es la integración con el ecosistema Spark. Flink es conveniente para streaming de baja latencia y procesamiento avanzado basado en eventos, destacándose por su manejo de estado y event time. Kafka Streams es una buena opción para aplicaciones que ya utilizan Kafka y necesitan procesamiento liviano directamente sobre sus topics, con la ventaja de integrarse de forma nativa con Kafka.

