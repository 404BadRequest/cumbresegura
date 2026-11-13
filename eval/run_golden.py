#!/usr/bin/env python3
"""Mide la cobertura de instrucciones de la v1 y la v2 sobre el golden set.

No llama a Gemini y no inventa informes. Comprueba que cada criterio exigido
esté escrito en el prompt y prueba el parser de veredicto con textos fijos.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main import detect_verdict, split_sections  # noqa: E402

CASES_PATH = ROOT / "eval" / "golden_set.json"
V1_PATH = ROOT / "prompts" / "v1_sistema_seguridad_montana.md"
V2_PATH = ROOT / "prompts" / "sistema_seguridad_montana.md"

CRITERIA = [
    {
        "id": "verdict",
        "label": "Veredicto categórico Go, condicionado o No Go",
        "needles": ["EXPEDICIÓN RECOMENDADA", "CONDICIONANTES", "NO RECOMENDADA"],
    },
    {
        "id": "eaws",
        "label": "Escala EAWS y problema nivológico",
        "needles": ["EAWS", "problema nivológico"],
    },
    {
        "id": "gear",
        "label": "Equipamiento técnico mínimo",
        "needles": ["piolet", "crampones"],
    },
    {
        "id": "turnaround",
        "label": "Ventana horaria y hora de retorno",
        "needles": ["ventana horaria", "turn-around"],
    },
    {
        "id": "missing",
        "label": "Pide ruta y nivel técnico si faltan",
        "needles": ["ruta precisa", "nivel técnico"],
    },
    {
        "id": "evidence",
        "label": "Prohíbe inventar datos, marca la estimación y la fecha fuera de ventana",
        "needles": ["No inventes", "estimación", "fuera de la ventana"],
    },
]


def prompt_body(path: Path) -> str:
    raw = path.read_text(encoding="utf-8")
    if "\n---\n" in raw:
        raw = raw.split("\n---\n", 1)[1]
    return raw


def criterion_passes(text: str, needles: list[str]) -> bool:
    folded = text.casefold()
    return all(needle.casefold() in folded for needle in needles)


def score(text: str, case_count: int) -> tuple[int, int, list[str]]:
    passed_criteria = []
    failed_criteria = []
    for criterion in CRITERIA:
        if criterion_passes(text, criterion["needles"]):
            passed_criteria.append(criterion["id"])
        else:
            failed_criteria.append(criterion["id"])
    points = len(passed_criteria) * case_count
    total = len(CRITERIA) * case_count
    return points, total, failed_criteria


def test_parser() -> None:
    go_report = """**1. Estado de la Nieve y Viabilidad del Ascenso:**
Manto estable, sin nieve reciente.

**2. Nivel de Riesgo General:**
Estimación EAWS nivel 1. Riesgo residual bajo.

**3. Recomendación Final y Criterio 'Go / No Go':**
[EXPEDICIÓN RECOMENDADA (Go)]
Ventana horaria de 6 a 11 h. Abortar si llega viento blanco.
"""
    verdict, _ = detect_verdict(go_report)
    if verdict != "go":
        raise SystemExit(f"El parser marcó un Go como {verdict}")
    sections = split_sections(go_report)
    if [section["number"] for section in sections] != [1, 2, 3]:
        raise SystemExit(f"Secciones inesperadas: {sections}")
    if "Manto estable" not in sections[0]["body"]:
        raise SystemExit("El cuerpo del apartado 1 no se separó del título")

    no_go = """**1. Estado:**
Placa de viento.

**2. Nivel:**
EAWS 4

**3. Recomendación:**
[NO RECOMENDADA / ABORTAR (No Go)]
"""
    if detect_verdict(no_go)[0] != "nogo":
        raise SystemExit("El parser no reconoció el No Go")

    conditional = "[RECOMENDADA CON CONDICIONANTES / RUTA ALTERNATIVA]"
    if detect_verdict(conditional)[0] != "conditional":
        raise SystemExit("El parser no reconoció el veredicto condicionado")


def main() -> None:
    test_parser()
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))["cases"]
    if len(cases) < 5:
        raise SystemExit("El golden set necesita al menos 5 casos")
    allowed = {"go", "conditional", "nogo"}
    for case in cases:
        verdict = case["expected"]["verdict"]
        if verdict not in allowed:
            raise SystemExit(f"{case['id']} tiene un veredicto desconocido: {verdict}")

    v1_points, total, v1_failed = score(prompt_body(V1_PATH), len(cases))
    v2_points, _, v2_failed = score(prompt_body(V2_PATH), len(cases))
    print(f"casos: {len(cases)}")
    print(f"criterios: {len(CRITERIA)}")
    print(f"v1: {v1_points}/{total}  fallos: {', '.join(v1_failed) or 'ninguno'}")
    print(f"v2: {v2_points}/{total}  fallos: {', '.join(v2_failed) or 'ninguno'}")
    print(f"mejora: {v2_points - v1_points} puntos de criterio por caso")
    if v2_points <= v1_points or v2_failed:
        raise SystemExit("La v2 no mejora la cobertura de la v1")


if __name__ == "__main__":
    main()
