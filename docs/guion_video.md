# Guion de video — 3 minutos

Hablar mirando la pantalla en la demo y a cámara en el problema y el cierre. No hace falta mostrar el código más de unos segundos.

## 0:00 a 0:30 — Problema

La noche anterior a una salida, el grupo tiene que decidir si sale. Mira la nieve de la semana, el viento del sábado y a qué hora hay que darse la vuelta. Eso hoy vive en tres pestañas y un chat. CumbreSegura lo junta en un informe: Go, condicionado o No Go.

## 0:30 a 0:45 — Para quién es

Sirve a quien planifica el ascenso: montañista, guía o club. No es un pronóstico más. El producto es la recomendación. El plan guía son 19 dólares al mes y el plan club, 49. Operar la beta cuesta del orden de 10 a 25 dólares al mes.

## 0:45 a 2:05 — Demo

Abrir la URL en una ventana de incógnito.

Decir: parto en Cerro El Plomo, 5.424 metros, y una fecha dentro de los próximos días. Completo la ruta de ejemplo y dejo el grupo en intermedio, porque sin esos datos el informe no cierra la evaluación.

Pulsar **Evaluar ascenso**.

Mientras carga: está leyendo los 14 días previos y los 7 que vienen, en Open-Meteo, a esa altitud.

Cuando aparezca el resultado, recorrer en este orden: la nieve acumulada y la ráfaga, el apartado de viabilidad, el nivel EAWS dicho como estimación, y el veredicto con la hora de retorno. Cerrar diciendo que la franja de arriba lo advierte: esto no es un boletín oficial.

## 2:05 a 2:40 — Cómo se construyó

Mostrar el repositorio, sin entrar en cada archivo.

El agente partió de `PROMPT_MAESTRO.md`: rol, requisitos, restricciones y criterios de aceptación. El prompt del informe está en `prompts/`. La v1 es el enunciado. La v2 le prohíbe inventar boletines y le obliga a decir cuando la fecha cae fuera del pronóstico. `eval/run_golden.py` mide esa mejora: 25 de 30 contra 30 de 30, sobre cinco casos. La clave de OpenAI no está en el repo. Va como secreto, con tope de gasto. Docker levanta el mismo servicio que se publica.

## 2:40 a 3:00 — Cierre

Repetir la URL. Una consulta, un veredicto, y el criterio queda escrito antes de salir de la casa.
