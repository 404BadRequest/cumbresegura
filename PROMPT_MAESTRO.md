# Prompt maestro — CumbreSegura

## Rol

Actúa como tech lead y desarrollador full-stack. Construye y deja listo para publicar un servicio web de seguridad en alta montaña. El producto se llama CumbreSegura.

## Objetivo

Una persona carga un cerro, coordenadas, altitud y fecha de ascenso. El sistema junta el clima real de los 14 días previos y de los 7 días siguientes, y un modelo de Gemini redacta un informe de viabilidad con un veredicto Go, condicionado o No Go.

La aplicación es el producto. Sin ese informe, no hay servicio.

## Requisitos

- Backend en Python con FastAPI, servido por Uvicorn.
- Frontend de una página, con la estructura visual de un dashboard Adminator: barra lateral, barra superior, tarjetas y formulario. Se comunica con el backend por `fetch`.
- Clima real de Open-Meteo: archivo histórico y pronóstico. La nieve se informa en centímetros, la precipitación en milímetros y el viento en km/h.
- Gemini mediante el SDK `google-genai`, con el system prompt de `prompts/sistema_seguridad_montana.md` inyectado como `system_instruction`. El modelo por defecto es `gemini-flash-latest`, configurable con `GEMINI_MODEL`.
- Formulario: cerro, latitud, longitud, altitud, fecha objetivo, ruta opcional y nivel técnico opcional.
- La respuesta visible tiene tres apartados y una insignia de veredicto.
- Si falta la ruta o el nivel del grupo, el informe lo dice.
- Si falta `GEMINI_API_KEY`, la clave es rechazada o se corta la red, la API responde un error claro y la pantalla lo muestra. Si el clima ya se obtuvo, igual se muestra.
- Aviso permanente: es una estimación académica, no un boletín oficial de avalanchas.
- Docker, `docker-compose.yml`, `vercel.json` y GitHub Actions.
- Documentación del curso: este archivo, `AGENTS.md`, `/prompts`, golden set de 5 casos, `README.md`, ficha de negocio y guion de video.

## Restricciones

- No dejes placeholders ni comentarios del tipo "resto del código aquí".
- No escribas claves, tokens ni `.env` en el repositorio. Solo `.env.example` con valores vacíos.
- No inventes series de clima: si Open-Meteo falla, se informa el fallo.
- No cambies la estructura de tres apartados ni los tres veredictos literales del prompt de sistema.
- No presentes el nivel EAWS como un boletín oficial.
- El workflow de GitHub se llama `.github/workflows/main.yml`. El CI corre en pull requests hacia `development`. El despliegue corre al hacer push a `main`, después del merge. La aprobación del dueño se documenta como regla de rama; el YAML no puede imponerla solo.

## Fases

1. Definir el contrato `POST /api/asesoria` y el error de clima o de Gemini.
2. Consultar Open-Meteo en paralelo y armar el JSON de contexto.
3. Llamar a Gemini con el prompt v2 y separar los tres apartados.
4. Dibujar el dashboard y los estados de carga, error y veredicto.
5. Empaquetar Docker, Vercel y el workflow.
6. Escribir el golden set y la comparación v1/v2.
7. Probar el flujo en el navegador.

## Criterios de aceptación

- `GET /api/health` responde `{"status":"ok"}` sin clave de Gemini.
- Una consulta con coordenadas válidas muestra las dos series de clima.
- Con `GEMINI_API_KEY` válida, el informe muestra los tres apartados y un veredicto Go, condicionado o No Go.
- Sin clave, la interfaz explica que falta `GEMINI_API_KEY` y no se cae en blanco.
- `docker compose up --build` publica el servicio en el puerto 8000.
- `python eval/run_golden.py` termina sin error y la v2 puntúa más que la v1.
- El repositorio no contiene secretos.
