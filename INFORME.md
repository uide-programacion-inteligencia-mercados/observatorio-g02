# Informe automático · G02 · El crédito del país

![Estado del robot](https://github.com/uide-programacion-inteligencia-mercados/observatorio-g02/actions/workflows/orquestador_diario.yml/badge.svg)

El robot escribe todos los días su propio informe en PDF: **`reports/informe_g02.pdf`**.
La insignia de arriba dice si la última corrida terminó bien (verde) o mal (rojo).

## Para quién es y qué decisión ayuda a tomar
**Lector:** Junta directiva y comité de riesgos

Ayuda al comité del banco a saber si la gente está pagando bien sus deudas o si debemos tener cuidado al prestar más dinero

## Qué dejamos fuera y por qué
Dejamos fuera datos como la inflación o el desempleo para enfocarnos únicamente en el crédito y los atrasos, porque menos datos hacen que el informe sea más fácil de entender

## Cuándo se lee
Se actualiza solito todos los días a las 5:00 a.m. para que la gerencia lo revise al empezar la jornada de trabajo

## Cómo sabemos que es confiable
Porque el robot revisa que los números del Banco Mundial sean lógicos y cuenta con un sistema que frena cualquier reporte incompleto para no mostrar información falsa

## Cómo se arma el informe
1. `robot_banco_mundial.py` trae los datos, los revisa con las reglas del equipo y los guarda.
2. `config_informe.json` tiene los textos del equipo (titular, lectura de negocio y recomendación).
3. `plantillas/informe.html.j2` es el molde con huecos que rellena Jinja2.
4. WeasyPrint imprime el PDF. Si el PDF sale roto, el portero lo rechaza y queda el informe anterior.
5. Reloj del robot: `0 10 * * *`
