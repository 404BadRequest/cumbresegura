# Alineación: lo pedido, lo mejorado y lo entregado

Este documento cierra el círculo entre el prompt técnico original (Gemini), la retroalimentación del Prompt Maestro (6 de noviembre de 2026) y la entrega final en este repositorio.

## 1. Cambio de modelo: Gemini → OpenAI

| Aspecto | Enunciado técnico original | Entrega final |
| --- | --- | --- |
| Proveedor | Google Gemini | OpenAI |
| Modelo pedido | `gemini-pro` | `gpt-4o-mini` (variable `OPENAI_MODEL`) |
| Clave | `GEMINI_API_KEY` | `OPENAI_API_KEY` (secreto en Vercel) |
| System prompt | Texto del PASO 4 | El mismo criterio Go / No Go, versionado en `/prompts` |

**Por qué.** El feedback del profesor ya advertía que `gemini-pro` está retirado y pedía un modelo vigente con buena relación costo/calidad. El equipo tenía clave de OpenAI disponible y la usó. El **prompt de sistema** (tres apartados, EAWS como estimación, veredictos literales) no depende del proveedor: es el mismo contrato de salida.

El enunciado técnico original se conserva en `prompt_t_cnico_para_agente_de_c_digo (1).md` para trazabilidad. El prompt que manda al agente hoy es `PROMPT_MAESTRO.md` y ya describe OpenAI.

## 2. Feedback del Prompt Maestro → qué se hizo

| Pedido del feedback (Grupo 1) | Estado en la entrega |
| --- | --- |
| Clima real, no mocks | Hecho. Open-Meteo archivo 14 días + pronóstico 7 días. |
| Modelo vigente (no `gemini-pro`) | Hecho. OpenAI `gpt-4o-mini`. |
| Prompt en `/prompts` con versiones | Hecho. `v1_...md` y `sistema_seguridad_montana.md` (v2). |
| Golden set de 5 casos y mejora medida | Hecho. `eval/golden_set.json`, `eval/run_golden.py`, `eval/resultados.md` (25/30 → 30/30). |
| `AGENTS.md` o `CLAUDE.md` | Hecho. `AGENTS.md`. |
| `README.md` con idea, uso y arquitectura | Hecho. |
| Dockerfile | Hecho. También `docker-compose.yml`. |
| Secretos fuera del repo y tope de gasto | Hecho. Clave solo en Vercel / `.env` local ignorado. README indica configurar tope en OpenAI. |
| Resolver Docker vs Vercel | Hecho. Vercel en producción; Docker para local y como alternativa (Fly/Cloud Run documentados). |
| Cliente e ingresos en la ficha | Hecho. `docs/ficha_negocio.pdf`. |
| Video ≤ 3 min | Hecho. `docs/video_presentacion.mp4`. |
| URL pública sin barreras | Hecho. https://cumbresegura.vercel.app |
| Fecha objetivo fuera de horizonte | Hecho en prompt v2 y en la lógica de la app. |
| EAWS como estimación, no boletín | Hecho en prompt v2 y aviso visible en la UI. |

## 3. Qué no se cambió a propósito

- Los **tres apartados** y los **tres veredictos literales** del system prompt.
- El producto sigue siendo un informe Go / No Go, no un dashboard genérico.
- El archivo técnico original con Gemini se dejó intacto como evidencia del punto de partida.

## 4. Cómo presentarlo al profesor en una frase

> Partimos del prompt técnico con Gemini Pro; el feedback pidió un modelo vigente y datos reales. Entregamos el mismo informe Go / No Go con Open-Meteo y OpenAI `gpt-4o-mini`, prompt versionado, golden set medido y la app en https://cumbresegura.vercel.app.
