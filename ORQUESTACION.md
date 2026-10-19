# Orquestación · G02 · El crédito del país

## Qué puede ir a la vez
Las consultas a las fuentes externas pueden ejecutarse en paralelo; por ejemplo, obtener datos de crédito y morosidad mientras se consulta otra fuente del observatorio. Luego se espera a que todas terminen para continuar con el análisis.

## Nuestro plan B
Si la fuente 1 no contesta,  el robot primero hace varios intentos con espera creciente, si después de eso sigue sin contestar, utiliza el último dato válido guardado como respaldo.

## Nuestra hora y por qué
Reloj: `0 10 * * *` (todos los días a las 10:00 UTC (05:00 en Quito))

10:00 UTC equivalente a las 5:00 am Quito, porque queremos que el robot recopile y procese la información antes de iniciar la jornada laboral.

## Qué guardamos cada día para comparar
Guardar cada día los valores más recientes de crédito al sector privado y morosidad bancaria, junto con la fecha de la corrida, para comparar su evolución entre hoy y mañana y detectar cambios o posibles tendencias.
