# Resiliencia · G02 · El crédito del país

![Estado del robot](https://github.com/uide-programacion-inteligencia-mercados/observatorio-g02/actions/workflows/orquestador_diario.yml/badge.svg)

La insignia de arriba dice si la última corrida del robot terminó bien (verde) o mal (rojo).

## Las reglas de calidad del robot
| Indicador | Mínimo creíble | Máximo creíble |
|---|---|---|
| Crédito al sector privado (% del PIB) | 5.0 | 120.0 |
| Morosidad bancaria (% de la cartera) | 0.0 | 25.0 |

- Filas mínimas: 10 · Antigüedad máxima del último dato: 4 años
- Reintentos: 3, con espera inicial de 2 s que se duplica en cada intento
- Reloj: `0 10 * * *`

## Qué es una falla para nosotros
Una falla es cuando el Banco Mundial no contesta tras varios intentos, cuando los datos llegan vacíos, o cuando un indicador sale de los rangos creíbles de la economía ecuatoriana (por ejemplo, una morosidad bancaria superior al 25%).

## Nuestro plan B
Si la fuente falla, el robot descarta los datos erróneos y conserva intactos los de la última corrida exitosa, evitando que el tablero muestre información absurda.

## Quién atiende la alerta
Cualquier integrante del equipo revisa la pestaña Issues de GitHub si llega la alerta roja y verifica el estado en la carpeta logs.

## Qué vigilamos cada lunes
Cada lunes revisamos el archivo salud_g02.csv para confirmar que los puntos verdes se mantengan estables y no existan advertencias.
