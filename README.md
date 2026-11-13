# CumbreSegura

Asesor de viabilidad para ascensos de alta montaña. Sitio publicado: [https://cumbresegura.vercel.app](https://cumbresegura.vercel.app).

La persona indica cerro, coordenadas, altitud y fecha. La aplicación reúne el clima de los 14 días previos y de los 7 días siguientes, y OpenAI redacta un informe con tres apartados y un veredicto: expedición recomendada, recomendada con condicionantes, o no recomendada.

Es una estimación académica a partir de meteorología. No es un boletín de avalanchas ni una autorización para salir.

## Idea

El cliente es quien planifica una salida: montañista, guía o club. El problema es decidir si se sale con datos repartidos entre pronósticos y sin un criterio único de nieve, viento y hora de retorno. La IA hace ese informe. Sin el veredicto, el producto no existe.

El detalle de cliente, precio y costo está en [docs/ficha_negocio.md](docs/ficha_negocio.md).

## Cómo usarlo

1. Abre la aplicación.
2. Revisa cerro, latitud, longitud, altitud y fecha. El formulario parte en Cerro El Plomo.
3. Si conoces la vía y el nivel del grupo, complétalos. Si no, el informe pedirá esos datos antes de cerrar la evaluación.
4. Pulsa **Evaluar ascenso**.
5. Lee la nieve, el viento y el veredicto. La hora de retorno y los motivos de aborto están en el tercer apartado.

Atajos del formulario: **Usar Cerro El Plomo**, **Usar Aconcagua** y **Completar ruta de ejemplo**.

## Arquitectura

```text
index.html  --POST /api/asesoria-->  FastAPI (main.py)
                                      |-- Open-Meteo archivo (14 días)
                                      |-- Open-Meteo pronóstico (7 días; si está saturado, usa la corrida previa)
                                      '-- OpenAI, system prompt v2
```

Archivos de ejecución:

- `main.py` — API, clima, OpenAI y parser del informe.
- `index.html` — dashboard.
- `prompts/sistema_seguridad_montana.md` — prompt v2, el que usa el servidor.
- `prompts/v1_sistema_seguridad_montana.md` — enunciado original, solo para comparar.
- `eval/golden_set.json` — cinco casos con entrada y resultado esperado.
- `eval/resultados.md` — mejora medida de la v1 a la v2.

`GET /api/health` responde sin llamar a OpenAI.

## Arranque local

Con Docker:

```bash
cp .env.example .env
# Edita .env y pega tu OPENAI_API_KEY. No la subas al repositorio.
docker compose up --build
```

Abre `http://localhost:8000`.

Sin Docker, con Python 3.12:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="tu-clave"
uvicorn main:app --host 0.0.0.0 --port 8000
```

Sin clave, el servicio igual arranca. La consulta trae el clima y explica que falta `OPENAI_API_KEY`.

Comprueba la rúbrica del prompt:

```bash
python eval/run_golden.py
```

## Secretos

`OPENAI_API_KEY` vive en el entorno o en el secreto de la plataforma. `OPENAI_MODEL` es opcional y parte en `gpt-4o-mini`. En la nube hay que configurar un límite de gasto en la API de OpenAI.

## Despliegue

Vercel detecta FastAPI porque `main.py` expone `app`. `vercel.json` solo alarga la función a 60 segundos, porque el informe tarda más que un request corto.

Secretos del repositorio para el workflow: `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`. También `OPENAI_API_KEY` en el proyecto de Vercel, no en GitHub.

```bash
npm install --global vercel
vercel link
vercel env add OPENAI_API_KEY production
vercel --prod
```

Si el plan de Vercel corta la función antes de que OpenAI responda, el mismo `Dockerfile` sirve en Fly.io o Cloud Run:

```bash
fly launch
fly secrets set OPENAI_API_KEY="tu-clave"
fly deploy
```

En Cloud Run se despliega la imagen y la clave se carga como variable de entorno del servicio, con tope de gasto en Google.

## GitHub

El pipeline está en `.github/workflows/main.yml`. El enunciado pedía ese nombre; en un paso anterior lo llamaba `deploy.yml`.

- Un pull request hacia `development` construye la imagen y comprueba `/api/health`.
- Un push a `main` construye la imagen y publica en Vercel.

En GitHub, la rama `main` queda protegida: solo entra por pull request y exige la aprobación del dueño del repositorio. Esa regla se configura en el repositorio; un workflow no puede imponerla por sí solo. `development` es la rama de integración.

## Ajustes respecto del prompt técnico

- El enunciado técnico pedía Gemini. El servicio publicado usa OpenAI (`gpt-4o-mini`, configurable con `OPENAI_MODEL`) porque esa es la clave disponible. El prompt de sistema es el mismo.
- El clima no es un mock. Open-Meteo no pide clave y el flujo se puede recorrer de punta a punta.

## Entrega del curso

- URL pública, cuando la clave y la plataforma estén configuradas.
- Este repositorio: README, Dockerfile, `PROMPT_MAESTRO.md`, `AGENTS.md`, `/prompts` y golden set.
- Guion del video de tres minutos: [docs/guion_video.md](docs/guion_video.md).
- Ficha de negocio de una página: [docs/ficha_negocio.md](docs/ficha_negocio.md). Para el PDF, ábrela en un visor e imprime en A4.
