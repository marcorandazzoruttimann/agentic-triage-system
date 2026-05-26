"""Client OpenAI: connessione e configurazione."""

from dotenv import dotenv_values
from openai import OpenAI

from paths import ENV_PATH

MODEL = "gpt-4.1-mini"


def _openai_api_key_from_dotenv() -> str | None:
    """Legge OPENAI_API_KEY solo dal file .env (non da os.environ)."""
    values = dotenv_values(ENV_PATH, interpolate=False)
    raw = values.get("OPENAI_API_KEY")
    if raw is None:
        return None
    key = str(raw).strip()
    return key or None


def get_client() -> OpenAI:
    """Client OpenAI con API key da .env in root repo."""
    api_key = _openai_api_key_from_dotenv()
    if not api_key:
        raise ValueError(
            f'API key non trovata in "{ENV_PATH}". Imposta OPENAI_API_KEY nel file.'
        )
    return OpenAI(api_key=api_key)
