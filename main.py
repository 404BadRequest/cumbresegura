"""CumbreSegura: informe Go / No Go para ascensos de alta montaña."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from google import genai
from google.genai import errors as genai_errors
from google.genai import types
from pydantic import BaseModel, Field, field_validator

ROOT = Path(__file__).resolve().parent
PROMPT_PATH = ROOT / "prompts" / "sistema_seguridad_montana.md"
INDEX_PATH = ROOT / "index.html"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
FORECAST_FALLBACK_URL = "https://previous-runs-api.open-meteo.com/v1/forecast"
DAILY_VARS = (
    "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,"
    "snowfall_sum,wind_speed_10m_max,wind_gusts_10m_max"
)
FORECAST_VARS = DAILY_VARS + ",cloud_cover_mean,uv_index_max"
DEFAULT_MODEL = "gemini-flash-latest"
HEADING_RE = re.compile(r"(?m)^\s*(?:\*\*)?\s*([123])\.\s+(.+)$")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cumbresegura")

app = FastAPI(title="CumbreSegura", version="1.0.0")


class AsesoriaError(Exception):
    def __init__(self, status: int, code: str, message: str, weather: dict | None = None):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.weather = weather


class AsesoriaRequest(BaseModel):
    mountain: str = Field(min_length=2, max_length=120)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    altitude_m: int = Field(ge=0, le=9000)
    target_date: date
    route: str | None = Field(default=None, max_length=300)
    group_level: str | None = Field(default=None, max_length=80)

    @field_validator("mountain", "route", "group_level", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str):
            cleaned = value.strip()
            return cleaned or None
        return value


def load_system_prompt() -> str:
    try:
        raw = PROMPT_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        raise AsesoriaError(
            500,
            "prompt_missing",
            "El prompt de sistema no está disponible en el servidor.",
        ) from exc
    if "\n---\n" in raw:
        raw = raw.split("\n---\n", 1)[1]
    text = raw.strip()
    if len(text) < 200:
        raise AsesoriaError(
            500,
            "prompt_missing",
            "El prompt de sistema no está disponible en el servidor.",
        )
    return text


def weather_label(code: int | None) -> str:
    if code is None:
        return "Sin dato"
    if code == 0:
        return "Despejado"
    if code in (1, 2, 3):
        return "Nublado parcial"
    if code in (45, 48):
        return "Niebla"
    if code in (51, 53, 55, 56, 57):
        return "Llovizna"
    if code in (61, 63, 65, 66, 67, 80, 81, 82):
        return "Lluvia"
    if code in (71, 73, 75, 77, 85, 86):
        return "Nieve"
    if code in (95, 96, 99):
        return "Tormenta"
    return f"Código {code}"


def _at(series: list | None, index: int):
    if not series or index >= len(series):
        return None
    value = series[index]
    if isinstance(value, float):
        return round(value, 1)
    return value


def _rows(daily: dict) -> list[dict]:
    days = daily.get("time") or []
    rows = []
    for index, day in enumerate(days):
        code = _at(daily.get("weather_code"), index)
        rows.append(
            {
                "date": day,
                "weather_code": code,
                "weather_label": weather_label(code if isinstance(code, int) else None),
                "temp_max_c": _at(daily.get("temperature_2m_max"), index),
                "temp_min_c": _at(daily.get("temperature_2m_min"), index),
                "precipitation_mm": _at(daily.get("precipitation_sum"), index),
                "snowfall_cm": _at(daily.get("snowfall_sum"), index),
                "wind_max_kmh": _at(daily.get("wind_speed_10m_max"), index),
                "gust_max_kmh": _at(daily.get("wind_gusts_10m_max"), index),
                "cloud_cover_pct": _at(daily.get("cloud_cover_mean"), index),
                "uv_index": _at(daily.get("uv_index_max"), index),
            }
        )
    return rows


def _numbers(rows: list[dict], key: str) -> list[float]:
    return [row[key] for row in rows if isinstance(row.get(key), (int, float))]


def _total(rows: list[dict], key: str) -> float | None:
    values = _numbers(rows, key)
    if not values:
        return None
    return round(sum(values), 1)


def _extreme(rows: list[dict], key: str, picker) -> float | None:
    values = _numbers(rows, key)
    if not values:
        return None
    return round(picker(values), 1)


def _summary(historical: list[dict], forecast: list[dict]) -> dict:
    return {
        "historical_snowfall_cm": _total(historical, "snowfall_cm"),
        "historical_precipitation_mm": _total(historical, "precipitation_mm"),
        "historical_min_temp_c": _extreme(historical, "temp_min_c", min),
        "historical_max_gust_kmh": _extreme(historical, "gust_max_kmh", max),
        "historical_snow_days": sum(
            1 for row in historical if isinstance(row.get("snowfall_cm"), (int, float)) and row["snowfall_cm"] > 0
        ),
        "forecast_snowfall_cm": _total(forecast, "snowfall_cm"),
        "forecast_precipitation_mm": _total(forecast, "precipitation_mm"),
        "forecast_min_temp_c": _extreme(forecast, "temp_min_c", min),
        "forecast_max_gust_kmh": _extreme(forecast, "gust_max_kmh", max),
        "forecast_max_cloud_pct": _extreme(forecast, "cloud_cover_pct", max),
        "forecast_days_with_gust_at_least_70": sum(
            1 for row in forecast if isinstance(row.get("gust_max_kmh"), (int, float)) and row["gust_max_kmh"] >= 70
        ),
        "units": {
            "snowfall": "cm",
            "precipitation": "mm",
            "temperature": "°C",
            "wind": "km/h",
            "cloud_cover": "%",
        },
    }


async def _get_json(client: httpx.AsyncClient, url: str, params: dict, attempts: int = 3) -> dict:
    headers = {"User-Agent": "CumbreSegura/1.0 (proyecto-academico)", "Accept": "application/json"}
    response = None
    for attempt in range(attempts):
        try:
            response = await client.get(url, params=params, headers=headers)
        except httpx.TimeoutException as exc:
            if attempt < attempts - 1:
                await asyncio.sleep(1.5 * (attempt + 1))
                continue
            raise AsesoriaError(
                504,
                "weather_timeout",
                "Open-Meteo no respondió a tiempo. Intenta de nuevo en unos segundos.",
            ) from exc
        except httpx.HTTPError as exc:
            raise AsesoriaError(
                502,
                "weather_unavailable",
                "No se pudo consultar el clima en Open-Meteo.",
            ) from exc
        if response.status_code in (429, 502, 503, 504) and attempt < attempts - 1:
            logger.warning("Open-Meteo %s respondió %s, reintento %s", url, response.status_code, attempt + 1)
            await asyncio.sleep(1.5 * (attempt + 1))
            continue
        break
    if response is None:
        raise AsesoriaError(502, "weather_unavailable", "No se pudo consultar el clima en Open-Meteo.")
    if response.status_code in (429, 502, 503, 504):
        logger.warning("Open-Meteo %s respondió %s", url, response.status_code)
        raise AsesoriaError(
            503,
            "weather_unavailable",
            "Open-Meteo está saturado en este momento. Intenta de nuevo en unos segundos.",
        )
    if response.status_code >= 400:
        logger.warning("Open-Meteo %s respondió %s", url, response.status_code)
        raise AsesoriaError(
            502,
            "weather_unavailable",
            "Open-Meteo rechazó la consulta. Revisa coordenadas y altitud.",
        )
    try:
        payload = response.json()
    except json.JSONDecodeError as exc:
        raise AsesoriaError(
            502,
            "weather_unavailable",
            "Open-Meteo devolvió una respuesta ilegible.",
        ) from exc
    if "daily" not in payload:
        raise AsesoriaError(
            502,
            "weather_unavailable",
            "Open-Meteo no entregó la serie diaria de clima.",
        )
    return payload


async def _forecast_payload(client: httpx.AsyncClient, params: dict) -> tuple[dict, str]:
    try:
        payload = await _get_json(client, FORECAST_URL, params, attempts=2)
        return payload, "Open-Meteo pronóstico"
    except AsesoriaError as exc:
        if exc.status != 503:
            raise
        logger.warning("Pronóstico principal saturado; usando la corrida previa de Open-Meteo")
    payload = await _get_json(client, FORECAST_FALLBACK_URL, params, attempts=2)
    return payload, "Open-Meteo pronóstico (corrida previa)"


async def fetch_weather(body: AsesoriaRequest) -> dict:
    today = datetime.now(timezone.utc).date()
    history_end = today - timedelta(days=1)
    history_start = history_end - timedelta(days=13)
    common = {
        "latitude": body.latitude,
        "longitude": body.longitude,
        "elevation": body.altitude_m,
        "timezone": "auto",
    }
    forecast_params = {**common, "forecast_days": 7, "daily": FORECAST_VARS}
    async with httpx.AsyncClient(timeout=20.0) as client:
        historical_payload, forecast_result = await asyncio.gather(
            _get_json(
                client,
                ARCHIVE_URL,
                {**common, "start_date": history_start.isoformat(), "end_date": history_end.isoformat(), "daily": DAILY_VARS},
            ),
            _forecast_payload(client, forecast_params),
        )
    forecast_payload, forecast_source = forecast_result
    historical = _rows(historical_payload["daily"])
    forecast = _rows(forecast_payload["daily"])
    forecast_dates = [row["date"] for row in forecast]
    return {
        "source": "Open-Meteo",
        "forecast_source": forecast_source,
        "elevation_m": historical_payload.get("elevation"),
        "timezone": forecast_payload.get("timezone"),
        "historical_period": {
            "start": history_start.isoformat(),
            "end": history_end.isoformat(),
        },
        "forecast_period": {
            "start": forecast_dates[0] if forecast_dates else None,
            "end": forecast_dates[-1] if forecast_dates else None,
        },
        "target_date": body.target_date.isoformat(),
        "target_date_inside_forecast": body.target_date.isoformat() in forecast_dates,
        "historical": historical,
        "forecast": forecast,
        "summary": _summary(historical, forecast),
    }


def build_user_contents(body: AsesoriaRequest, weather: dict) -> str:
    payload = {
        "consulta": {
            "cerro": body.mountain,
            "latitud": body.latitude,
            "longitud": body.longitude,
            "altitud_m": body.altitude_m,
            "fecha_objetivo": body.target_date.isoformat(),
            "ruta": body.route,
            "nivel_tecnico_del_grupo": body.group_level,
        },
        "clima": weather,
        "notas": [
            "No hay perfil de nieve, test de columna ni boletín de avalanchas en estos datos.",
            "La nieve está en centímetros, la precipitación en milímetros y el viento en km/h.",
            "Si ruta o nivel_tecnico_del_grupo es null, faltan esos datos.",
            "Si target_date_inside_forecast es false, la fecha objetivo está fuera de la ventana del pronóstico.",
            "Si forecast_source menciona corrida previa, el pronóstico es real pero de una pasada anterior del modelo, porque el servicio principal estaba saturado.",
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _map_gemini_error(exc: Exception) -> AsesoriaError:
    code = getattr(exc, "code", None)
    text = str(exc).lower()
    if code in (401, 403) or "api key" in text or "permission" in text or "unauthenticated" in text:
        return AsesoriaError(
            401,
            "invalid_api_key",
            "La clave de Gemini fue rechazada. Revisa GEMINI_API_KEY en el entorno.",
        )
    if code == 429 or "resource_exhausted" in text or "quota" in text:
        return AsesoriaError(
            429,
            "gemini_quota",
            "La API de Gemini alcanzó su límite de uso. Revisa el tope de gasto o intenta más tarde.",
        )
    if "timeout" in text or "deadline" in text or code == 504:
        return AsesoriaError(
            504,
            "gemini_timeout",
            "Gemini no respondió a tiempo. Intenta de nuevo.",
        )
    logger.exception("Fallo al generar el informe")
    return AsesoriaError(
        502,
        "gemini_error",
        "No se pudo generar el informe. El servicio de IA no respondió.",
    )


def generate_report(contents: str) -> tuple[str, str]:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise AsesoriaError(
            503,
            "missing_api_key",
            "Falta GEMINI_API_KEY. Configúrala como secreto del entorno, nunca dentro del repositorio.",
        )
    model = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=load_system_prompt(),
                temperature=0.3,
                max_output_tokens=4096,
            ),
        )
    except AsesoriaError:
        raise
    except genai_errors.APIError as exc:
        raise _map_gemini_error(exc) from exc
    except Exception as exc:
        raise _map_gemini_error(exc) from exc
    text = (getattr(response, "text", None) or "").strip()
    if not text:
        raise AsesoriaError(
            502,
            "empty_report",
            "Gemini respondió sin texto. Intenta de nuevo.",
        )
    return text, model


def _clean_heading(raw: str) -> tuple[str, str]:
    title = raw.replace("**", "").strip()
    inline = ""
    if ":" in title:
        title, inline = title.split(":", 1)
    return title.strip(" *"), inline.strip()


def split_sections(text: str) -> list[dict]:
    matches = list(HEADING_RE.finditer(text))
    if len(matches) < 3:
        return [{"number": 1, "title": "Informe", "body": text.strip()}]
    found: dict[int, dict] = {}
    for index, match in enumerate(matches):
        number = int(match.group(1))
        if number in found:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        title, inline = _clean_heading(match.group(2))
        following = text[match.end() : end].strip()
        body = "\n\n".join(part for part in (inline, following) if part)
        found[number] = {"number": number, "title": title, "body": body}
    ordered = [found[number] for number in (1, 2, 3) if number in found]
    return ordered or [{"number": 1, "title": "Informe", "body": text.strip()}]


def detect_verdict(text: str) -> tuple[str, str]:
    folded = text.upper().replace("Ó", "O").replace("Í", "I")
    bracketed = re.findall(r"\[[^\[\]\n]{0,160}\]", folded)
    candidates = ["\n".join(bracketed), folded] if bracketed else [folded]
    for blob in candidates:
        if "NO RECOMENDADA" in blob:
            return "nogo", "No recomendada / Abortar (No Go)"
        if "CONDICIONANTE" in blob or "RUTA ALTERNATIVA" in blob:
            return "conditional", "Recomendada con condicionantes"
        if "EXPEDICION RECOMENDADA" in blob:
            return "go", "Expedición recomendada (Go)"
    return "unknown", "Veredicto no identificado"


def _check_target_date(body: AsesoriaRequest) -> None:
    today = datetime.now(timezone.utc).date()
    if body.target_date < today - timedelta(days=1) or body.target_date > today + timedelta(days=120):
        raise AsesoriaError(
            422,
            "invalid_date",
            "La fecha objetivo debe estar entre ayer y los próximos 120 días.",
        )


@app.exception_handler(AsesoriaError)
async def handle_asesoria(_: Request, exc: AsesoriaError) -> JSONResponse:
    body: dict = {"error": {"code": exc.code, "message": exc.message}}
    if exc.weather is not None:
        body["weather"] = exc.weather
    return JSONResponse(status_code=exc.status, content=body)


@app.exception_handler(RequestValidationError)
async def handle_validation(_: Request, __: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "invalid_input",
                "message": "Revisa el formulario. El cerro, las coordenadas, la altitud y la fecha tienen que ser válidos.",
            }
        },
    )


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "service": "cumbresegura"}


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(INDEX_PATH, media_type="text/html; charset=utf-8")


@app.post("/api/asesoria")
async def asesoria(body: AsesoriaRequest) -> dict:
    _check_target_date(body)
    weather = await fetch_weather(body)
    contents = build_user_contents(body, weather)
    try:
        report, model = await asyncio.to_thread(generate_report, contents)
    except AsesoriaError as exc:
        exc.weather = weather
        raise
    verdict, verdict_label = detect_verdict(report)
    return {
        "verdict": verdict,
        "verdict_label": verdict_label,
        "sections": split_sections(report),
        "report": report,
        "weather": weather,
        "meta": {
            "model": model,
            "mountain": body.mountain,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        },
    }
