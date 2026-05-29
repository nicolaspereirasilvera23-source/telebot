import unicodedata

from models.lead import Lead


LATAM_COUNTRIES = [
    "argentina",
    "bolivia",
    "brasil",
    "brazil",
    "chile",
    "colombia",
    "costa rica",
    "cuba",
    "ecuador",
    "el salvador",
    "guatemala",
    "honduras",
    "mexico",
    "nicaragua",
    "panama",
    "paraguay",
    "peru",
    "dominicana",
    "uruguay",
    "venezuela",
]


def qualify_lead(lead: Lead) -> Lead:
    """
    Aplica las reglas ICP en Python y actualiza si el lead califica.
    """
    failed_reasons: list[str] = []

    if not _is_services_company(lead.company_type):
        failed_reasons.append("no parece ser una empresa de servicios o consultoria")

    if lead.employees is None or lead.employees < 5:
        failed_reasons.append("no llega al minimo de 5 empleados")

    if not _is_target_location(lead.location):
        failed_reasons.append("no esta en Espana o Latinoamerica")

    if not _has_ai_or_automation_interest(lead.interest):
        failed_reasons.append("no muestra interes claro en automatizacion o IA")

    lead.qualified = len(failed_reasons) == 0

    if lead.qualified:
        lead.reason = "Cumple con el ICP: servicios/consultoria, minimo 5 empleados, ubicacion objetivo e interes en automatizacion o IA."
    else:
        lead.reason = "No cumple con el ICP porque " + ", ".join(failed_reasons) + "."

    return lead


def _normalize(value: str | None) -> str:
    # Normaliza texto para comparar igual palabras con o sin tildes.
    text = (value or "").lower().strip()
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _is_services_company(company_type: str | None) -> bool:
    text = _normalize(company_type)
    keywords = ["servicio", "servicios", "consultoria", "agency", "agencia"]
    return any(keyword in text for keyword in keywords)


def _is_target_location(location: str | None) -> bool:
    text = _normalize(location)
    if "espana" in text or "spain" in text:
        return True

    return any(country in text for country in LATAM_COUNTRIES)


def _has_ai_or_automation_interest(interest: str | None) -> bool:
    text = _normalize(interest)
    keywords = ["automatizacion", "automacion", "ia", "ai", "inteligencia artificial"]
    return any(keyword in text for keyword in keywords)
