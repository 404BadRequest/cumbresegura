# Mejora del prompt v1 a v2

La v1 es el enunciado original (`prompts/v1_sistema_seguridad_montana.md`). La v2 es la que usa la aplicación (`prompts/sistema_seguridad_montana.md`).

Esta medición no simula respuestas del modelo. Recorre los 5 casos del golden set y cuenta si el prompt escribe cada criterio. Cada criterio aplica a cada caso, así que el máximo es 6 criterios × 5 casos = 30.

Se recalcula con:

```bash
python eval/run_golden.py
```

## Rúbrica

1. Veredicto categórico Go, condicionado o No Go.
2. Escala EAWS y problema nivológico.
3. Equipamiento técnico mínimo.
4. Ventana horaria y hora de retorno.
5. Pedir ruta precisa y nivel técnico si faltan.
6. Prohibir datos inventados, declarar que el EAWS es una estimación y decir "fuera de la ventana" si la fecha no entra en el pronóstico.

## Resultado

| Versión | Puntos | Qué falta |
| --- | --- | --- |
| v1 | 25/30 | El criterio 6, en los cinco casos |
| v2 | 30/30 | Nada de la rúbrica |
| Mejora | +5 | +17 puntos porcentuales (83% a 100%) |

La v1 ya obligaba la estructura, el EAWS, el equipo, el horario y la advertencia si faltan ruta o nivel. No impedía que el modelo rellenara un perfil de nieve o un boletín que Open-Meteo no entrega, ni le decía qué hacer cuando la fecha objetivo cae fuera de los siete días de pronóstico.

## Qué cambia en cada caso

- GS-01 Ventana estable. El veredicto esperado es Go. La v2 exige citar centímetros de nieve, °C y km/h, y decir que el nivel EAWS es una estimación.
- GS-02 Nevada y viento. El veredicto esperado es No Go por placa de viento. La v2 no permite inventar un test de columna para sostener ese No Go: tiene que salir de la nieve reciente y las ráfagas del JSON.
- GS-03 Terreno glaciar. El veredicto esperado es condicionado, con piolet, crampones y autorrescate en grietas. Esos equipos ya estaban en la v1; la v2 añade que el hielo se lee desde la ruta y el clima, no desde un perfil observado.
- GS-04 Sin ruta ni nivel. Las dos versiones piden esos datos para una evaluación definitiva. La v2, además, no puede completarlos por su cuenta.
- GS-05 Viento blanco. El veredicto esperado es No Go. Si la fecha de salida no está en los siete días, la v2 tiene que decir "fuera de la ventana" en lugar de describir ese día.

El resultado esperado de cada entrada está en `golden_set.json`. La app publicada en https://cumbresegura.vercel.app usa OpenAI (`gpt-4o-mini`) con ese prompt v2; el formulario es el banco de prueba con la entrada de cada caso.

Nota de proveedor: el enunciado original hablaba de Gemini. La medición v1→v2 es del **texto del system prompt**, independiente del LLM. En producción el proveedor es OpenAI; ver `docs/alineacion_entrega.md`.
