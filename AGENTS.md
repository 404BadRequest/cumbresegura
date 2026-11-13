# Reglas para agentes en CumbreSegura

- El producto es un informe Go / No Go. No agregues funciones que no entren en ese flujo.
- El LLM de producción es OpenAI (`OPENAI_API_KEY`, modelo `OPENAI_MODEL` / `gpt-4o-mini`). El enunciado original pedía Gemini; no reviertas a Gemini sin actualizar `PROMPT_MAESTRO.md`, `README.md` y `docs/alineacion_entrega.md`.
- El prompt que ejecuta la aplicación es `prompts/sistema_seguridad_montana.md`. Si lo cambias, actualiza `eval/resultados.md` y deja la versión anterior rastreable.
- No inventes clima, boletines ni perfiles de nieve. Los números salen de Open-Meteo.
- La nieve se expresa en centímetros, la precipitación en milímetros y el viento en km/h.
- No escribas `OPENAI_API_KEY`, tokens de Vercel ni archivos `.env` en el repositorio.
- Mantén los tres apartados y los tres veredictos literales del prompt de sistema.
- Si cambias el texto del informe, conserva el parser de `detect_verdict` y `split_sections`, y ejecuta `python eval/run_golden.py`.
- La pantalla debe seguir mostrando un error comprensible cuando falle la clave o la red.
- El aviso de que esto no es un boletín oficial permanece visible.
