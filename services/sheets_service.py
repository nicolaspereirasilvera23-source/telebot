import os
from datetime import datetime
from zoneinfo import ZoneInfo

import requests


APPS_SCRIPT_URL = os.getenv("GOOGLE_APPS_SCRIPT_URL")
TIMEZONE = os.getenv("APP_TIMEZONE", "America/Montevideo")


def log_lead(raw_text: str, result: dict) -> bool:
    """
    Envia el lead procesado a Google Apps Script sin cortar el flujo del bot.
    """
    try:
        if not APPS_SCRIPT_URL:
            raise ValueError("Falta GOOGLE_APPS_SCRIPT_URL en el archivo .env")

        payload = _build_payload(raw_text, result)
        response = requests.post(APPS_SCRIPT_URL, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as error:
        print(f"[Sheets] No se pudo guardar el lead: {error}")
        return False


def _build_payload(raw_text: str, result: dict) -> dict[str, str]:
    # Arma el payload que Apps Script recibe y escribe en Google Sheets.
    now = datetime.now(ZoneInfo(TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
    decision = "Cualificado" if result.get("qualified") else "No cualificado"
    reason = str(result.get("reason", "Sin motivo informado."))

    return {
        "fecha": now,
        "lead_recibido": raw_text,
        "decision": decision,
        "motivo": reason,
    }
