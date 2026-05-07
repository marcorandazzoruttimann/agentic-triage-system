from pydantic import BaseModel, Field, field_validator
from typing import Literal


# Categorie consentite (vincolo forte)
Category = Literal["IT", "BILLING", "SALES", "SECURITY"]

# Priorità consentite
Priority = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


class Ticket(BaseModel):
    """
    Modello dati del ticket per il sistema di triage.
    Questo schema rappresenta l'output finale dell'agente AI.
    """

    categoria: Category = Field(
        ...,
        description="Categoria del ticket (IT, BILLING, SALES, SECURITY)"
    )

    priorita: Priority = Field(
        ...,
        description="Livello di priorità del ticket"
    )

    riassunto_breve: str = Field(
        ...,
        description="Riassunto sintetico (max 15 parole)"
    )

    messaggio_originale: str = Field(
        ...,
        description="Testo originale del ticket utente"
    )

    @field_validator("riassunto_breve")
    @classmethod
    def validate_riassunto_length(cls, value: str) -> str:
        """
        Valida che il riassunto non superi le 15 parole.
        """
        word_count = len(value.strip().split())
        if word_count > 15:
            raise ValueError(
                f"Il riassunto supera il limite di 15 parole ({word_count})"
            )
        return value

    @field_validator("messaggio_originale")
    @classmethod
    def validate_messaggio_not_empty(cls, value: str) -> str:
        """
        Evita messaggi vuoti o non validi.
        """
        if not value or not value.strip():
            raise ValueError("Il messaggio originale non può essere vuoto")
        return value