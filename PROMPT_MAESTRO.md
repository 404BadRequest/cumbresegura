# Prompt maestro — CumbreSegura

## Origen y desviación del enunciado técnico

El enunciado técnico del equipo (`prompt_t_cnico_para_agente_de_c_digo (1).md`) pedía Google Gemini (`gemini-pro`). Ese identificador está retirado y el feedback del Prompt Maestro (6 nov 2026) pidió un modelo vigente. La entrega usa **OpenAI** (`gpt-4o-mini`, `OPENAI_API_KEY` / `OPENAI_MODEL`) porque esa es la clave disponible. El **system prompt** Go / No Go es el mismo contrato de salida; solo cambia el proveedor del LLM. La tabla completa está en `docs/alineacion_entrega.md`.

## Rol

Actúa como tech lead y desarrollador full-stack. Construye y deja listo para publicar un servicio web de seguridad en alta montaña. El producto se llama CumbreSegura.

## Objetivo

Una persona carga un cerro, coordenadas, altitud y fecha de ascenso. El sistema junta el clima real de los 14 días previos y de los 7 días siguientes, y un modelo de OpenAI redacta un informe de viabilidad con un veredicto Go, condicionado o No Go.

La aplicación es el producto. Sin ese informe, no hay servicio.

## Requisitos

- Backend en Python con FastAPI, servido por Uvicorn.
- Frontend de una página, con la estructura visual de un dashboard Adminator: barra lateral, barra superior, tarjetas y formulario. Se comunica con el backend por `fetch`.
- Clima real de Open-Meteo: archivo histórico y pronóstico. La nieve se informa en centímetros, la precipitación en milímetros y el viento en km/h.
- OpenAI mediante el SDK oficial, con el system prompt de `prompts/sistema_seguridad_montana.md` como mensaje de sistema. El modelo por defecto es `gpt-4o-mini`, configurable con `OPENAI_MODEL`.
- Formulario: cerro, latitud, longitud, altitud, fecha objetivo, ruta opcional y nivel técnico opcional.
- La respuesta visible tiene tres apartados y una insignia de veredicto.
- Si falta la ruta o el nivel del grupo, el informe lo dice.
- Si falta `OPENAI_API_KEY`, la clave es rechazada o se corta la red, la API responde un error claro y la pantalla lo muestra. Si el clima ya se obtuvo, igual se muestra.
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

1. Definir el contrato `POST /api/asesoria` y el error de clima o de OpenAI.
2. Consultar Open-Meteo en paralelo y armar el JSON de contexto.
3. Llamar a OpenAI con el prompt v2 y separar los tres apartados.
4. Dibujar el dashboard y los estados de carga, error y veredicto.
5. Empaquetar Docker, Vercel y el workflow.
6. Escribir el golden set y la comparación v1/v2.
7. Probar el flujo en el navegador.

## Criterios de aceptación

- `GET /api/health` responde `{"status":"ok"}` sin clave de OpenAI.
- Una consulta con coordenadas válidas muestra las dos series de clima.
- Con `OPENAI_API_KEY` válida, el informe muestra los tres apartados y un veredicto Go, condicionado o No Go.
- Sin clave, la interfaz explica que falta `OPENAI_API_KEY` y no se cae en blanco.
- `docker compose up --build` publica el servicio en el puerto 8000.
- `python eval/run_golden.py` termina sin error y la v2 puntúa más que la v1.
- El repositorio no contiene secretos.
