# services/llm_service.py

import json
import os
import re

from google import genai
from models.lead import Lead
from services.qualifier_service import qualify_lead

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")


def analyze_lead(raw_text: str) -> dict:
    """
    Recibe el mensaje libre del lead, extrae datos con el proveedor configurado
    y aplica las reglas ICP en Python.
    """
    if LLM_PROVIDER == "mock":
        # Mock evita llamadas externas y permite probar Telegram/Sheets sin cuota LLM.
        return _analyze_lead_with_mock(raw_text)

    client = _get_gemini_client()

    if client is None:
        return _analyze_lead_with_mock(raw_text)

    prompt = f"""
Sos un analista de leads B2B.
Analiza este lead y devolve SOLO un JSON valido, sin markdown ni explicaciones.

ICP:
- Empresa de servicios o consultoria.
- Minimo 5 empleados.
- Espana o Latinoamerica.
- Interes en automatizacion o IA.

Texto del lead:
"{raw_text}"

Responde con este formato exacto:
{{
  "company_type": "string o null",
  "employees": number o null,
  "location": "string o null",
  "interest": "string o null"
}}
"""

    try:
        response = client.models.generate_content(
            # El modelo queda configurable para cambiarlo sin tocar codigo.
            model=GEMINI_MODEL,
            contents=prompt,
        )

        # Gemini devuelve texto JSON y lo convertimos a diccionario Python.
        content = response.text

        if content is None:
            raise ValueError("Gemini no devolvio contenido")

        lead_data = json.loads(content)
    except Exception:
        # Fallback local para que el bot siga funcionando si Gemini no tiene cuota.
        return _analyze_lead_with_mock(raw_text)

    return _qualify_lead_data(lead_data)


def _analyze_lead_with_mock(raw_text: str) -> dict:
    # Mock analiza ejemplos simples con reglas locales y devuelve el formato final.
    lead_data = _extract_lead_locally(raw_text)
    return _qualify_lead_data(lead_data)


def _qualify_lead_data(lead_data: dict) -> dict:
    # Convierte datos extraidos a Lead y aplica la decision del ICP.
    lead = Lead.from_dict(lead_data)
    qualified_lead = qualify_lead(lead)
    return qualified_lead.to_dict()


def _get_gemini_client():
    # Crea el cliente solo cuando hay API key disponible.
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return None

    return genai.Client(api_key=api_key)


def _extract_lead_locally(raw_text: str) -> dict:
    """
    Extrae datos basicos sin LLM para poder probar el bot completo.
    """
    text = raw_text.lower()

    return {
        "company_type": _detect_company_type(text),
        "employees": _detect_employees(text),
        "location": _detect_location(text),
        "interest": _detect_interest(text),
    }


def _detect_company_type(text: str) -> str | None:
    # Detecta rubro usando palabras clave simples del ICP.
    if any(keyword in text for keyword in ["consultoria", "consultoría", "servicio", "servicios", "agencia"]):
        return "servicios o consultoria"

    return None


def _detect_employees(text: str) -> int | None:
    # Busca cantidades tipo "12 empleados" o "equipo de 8".
    match = re.search(r"(\d+)\s*(empleados|personas|colaboradores)", text)

    if match:
        return int(match.group(1))

    match = re.search(r"equipo de\s*(\d+)", text)

    if match:
        return int(match.group(1))

    return None


def _detect_location(text: str) -> str | None:
    # Reconoce paises objetivo frecuentes para el challenge.
    locations = [
        "argentina",
        "chile",
        "colombia",
        "espana",
        "españa",
        "mexico",
        "méxico",
        "peru",
        "perú",
        "uruguay",
    ]

    for location in locations:
        if location in text:
            return location

    return None


def _detect_interest(text: str) -> str | None:
    # Detecta interes en IA o automatizacion con palabras clave directas.
    if any(keyword in text for keyword in ["automatizacion", "automatización", "ia", "ai", "inteligencia artificial"]):
        return "automatizacion o IA"

    return None
