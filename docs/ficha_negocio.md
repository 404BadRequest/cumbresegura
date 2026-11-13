# Ficha de negocio — CumbreSegura

**Cliente.** Montañista, guía o club que decide si un ascenso se hace, se cambia o se suspende. No es un servicio para turismo general ni para pronóstico de ciudad.

**Problema.** La decisión junta nieve reciente, viento, visibilidad y hora de retorno. Esos datos están repartidos y el grupo suele resolverlo por chat, la noche anterior. Un error sale caro y un pronóstico suelto no dice si se sale.

**Propuesta.** CumbreSegura arma un informe de una lectura: clima de 14 días atrás, pronóstico de 7 días y un veredicto Go, condicionado o No Go, con equipo mínimo y hora de retorno. La IA es el producto. Sin ese informe no hay nada que cobrar.

**Ingresos.** Tres consultas gratis al mes para probar. Plan guía: 19 USD al mes, informes para su cartera de salidas. Plan club: 49 USD al mes, varias cuentas y el mismo criterio para todo el grupo. El precio se cobra por la decisión escrita, no por el acceso al clima, que sigue siendo público.

**Costo mensual de operar la beta.** Open-Meteo: 0 USD. OpenAI (`gpt-4o-mini`), unas 200 consultas: 8 a 15 USD. Hosting en el plan gratuito de Vercel, o cerca de 5 USD si hay que pasar a Fly.io o Cloud Run porque la función se corta. Dominio, prorrateado: cerca de 1 USD. Total estimado: 10 a 25 USD al mes mientras el uso siga en esa beta. La clave de la API lleva un tope de gasto para que una ráfaga de consultas no dispare la cuenta.

**Límite que se dice en el producto.** El informe es una estimación meteorológica. No reemplaza el boletín de avalanchas ni el juicio de quien va a terreno.
