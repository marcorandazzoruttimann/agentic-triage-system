from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

Category = Literal["IT", "BILLING", "SALES", "SECURITY"]
Priority = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
TicketStatus = Literal["OPEN", "TRIAGED"]


class TriageResult(BaseModel):
    """Output strutturato dell'LLM (Parte 1)."""

    categoria: Category
    priorita: Priority
    riassunto_breve: str
    messaggio_originale: str

    @field_validator("riassunto_breve")
    @classmethod
    def validate_riassunto_length(cls, value: str) -> str:
        word_count = len(value.strip().split())
        if word_count > 15:
            raise ValueError(
                f"Il riassunto supera il limite di 15 parole ({word_count})"
            )
        return value

    @field_validator("messaggio_originale")
    @classmethod
    def validate_messaggio_not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Il messaggio originale non può essere vuoto")
        return value


class Ticket(BaseModel):
    """Ticket persistente con ciclo di vita (Parte 2)."""

    id: int
    status: TicketStatus
    messaggio_originale: str
    categoria: Category | None = None
    priorita: Priority | None = None
    riassunto_breve: str | None = None
    team: str | None = None

    @field_validator("messaggio_originale")
    @classmethod
    def validate_messaggio_not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Il messaggio originale non può essere vuoto")
        return value

    @model_validator(mode="after")
    def validate_triaged_fields(self) -> "Ticket":
        if self.status == "TRIAGED":
            missing = []
            if self.categoria is None:
                missing.append("categoria")
            if self.priorita is None:
                missing.append("priorita")
            if not self.riassunto_breve:
                missing.append("riassunto_breve")
            if missing:
                raise ValueError(
                    f"Ticket TRIAGED incompleto: campi mancanti {', '.join(missing)}"
                )
        return self
