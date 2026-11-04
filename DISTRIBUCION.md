# Distribución del informe · Equipo G02

## 1. ¿A quién le llega el informe y por qué?
Le llega a la junta directiva y al comité de riesgos del banco. Con este informe deciden si pueden seguir prestando con los mismos criterios o si deben ajustar los requisitos de aprobación de créditos porque la morosidad empieza a subir. Por eso el informe muestra el crédito al sector privado junto con la morosidad: lo que importa no es solo cuánto se presta, sino si la gente está pagando.

## 2. ¿Por qué ese canal y no otro?
Usamos un canal de chat (Slack, #informes-g02). Seguimos la regla «el chat avisa, el correo entrega, la alerta protege»: el mensaje en el chat avisa que hay un informe nuevo, ya trae el titular y el estado del robot, y tiene el enlace al PDF completo. No usamos correo porque tendríamos que guardar los correos de las personas y una contraseña de correo, y eso son más datos sensibles que cuidar; con el chat basta un solo secreto. Si el comité necesitara archivar el PDF adjunto, se podría agregar el correo después. La alerta en Issues de GitHub es la que protege: avisa al equipo cuando el envío falla.

## 3. ¿Cuándo llega?
- Día y hora de Quito: lunes a las 08:17.
- Línea de cron en UTC: `17 13 * * 1`
- La cuenta: Quito está 5 horas detrás de UTC, entonces 08:17 + 5 h = 13:17 UTC. No pasa de las 24 horas, así que sigue siendo lunes.
- Por qué esa hora: el comité de riesgos revisa la situación al inicio de la semana, antes de aprobar créditos nuevos. Lo mandamos una vez por semana y no todos los días porque los datos del Banco Mundial cambian una vez al año; mandarlo diario solo llenaría el chat con lo mismo. Usamos el minuto 17 para no caer en la hora en punto, cuando GitHub está saturado.
- Algo que vimos: GitHub a veces retrasa varias horas la corrida diaria del robot. Si el lunes el robot todavía no corrió, llega el informe del día anterior, que sigue sirviendo porque los datos son anuales. Si el informe tuviera más de 2 días, el mensaje avisa «OJO: informe de hace X días».

## 4. ¿Qué pasa si el envío falla?
El cartero distingue dos tipos de error. Un error pasajero (Slack ocupado o un corte de internet) puede arreglarse solo, así que el cartero reintenta hasta 3 veces, esperando 1 y luego 2 segundos. Un error permanente (por ejemplo, el webhook fue borrado y Slack responde 404) no se arregla reintentando, así que no insiste. En los dos casos anota «fallido» en logs/envios_g02.jsonl, la corrida sale en rojo y se abre la alerta «🚨 No se pudo hacer llegar el informe» en Issues. Cualquier integrante del equipo que la vea revisa la corrida y la línea que empieza con RESULTADO. El informe no se pierde ni se toca: sigue guardado en reports/. Cuando un envío real vuelve a funcionar, la alerta se cierra sola. Además, el cartero no manda dos veces el mismo informe el mismo día («omitido»), para no llenar el chat. Todo esto lo probamos con el simulacro.

## 5. Privacidad y secretos
La dirección del webhook es una llave: quien la tenga puede escribir en nuestro canal. Por eso está guardada solo en GitHub Secrets con el nombre SLACK_WEBHOOK_URL, y no está escrita en ningún archivo de la casa; GitHub tampoco la muestra en los registros de las corridas. Si se filtrara (por ejemplo, en un chat o en una captura), crearíamos una dirección nueva en Slack, borraríamos la anterior para que deje de funcionar y actualizaríamos el secreto; borrar el mensaje no basta. El informe solo usa datos agregados del país (crédito y morosidad del Banco Mundial), no datos de clientes. El mensaje y la bitácora no llevan nombres, correos ni contraseñas, y el canal solo tiene a los integrantes del equipo.

## Uso de IA
Usamos Claude como apoyo para entender la guía y revisar los pasos. Las decisiones del canal, la hora y el lector son del equipo.
