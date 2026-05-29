from dataclasses import dataclass
from typing import Any


@dataclass
class Lead:
    company_type: str | None
    employees: int | None
    location: str | None
    interest: str | None
    qualified: bool = False
    reason: str = "Pendiente de calificacion."

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Lead":
        """
        Convierte el JSON ya parseado de OpenAI en un objeto Lead.
        """
        return cls(
            company_type=data.get("company_type"),
            employees=_parse_employees(data.get("employees")),
            location=data.get("location"),
            interest=data.get("interest"),
            qualified=bool(data.get("qualified", False)),
            reason=str(data.get("reason", "Sin motivo informado.")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "company_type": self.company_type,
            "employees": self.employees,
            "location": self.location,
            "interest": self.interest,
            "qualified": self.qualified,
            "reason": self.reason,
        }


def _parse_employees(value: Any) -> int | None:
    if value is None:
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None
