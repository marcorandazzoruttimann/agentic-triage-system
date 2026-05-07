import os
from openai import OpenAI


# Inizializzazione client OpenAI
def get_client() -> OpenAI:
    """
    Crea e restituisce un client OpenAI utilizzando la API key da variabile d'ambiente.
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("API key non trovata. Assicurati di aver configurato .env")

    return OpenAI(api_key=api_key)


def call_llm(prompt: str) -> str:
    """
    Invia un prompt al modello e restituisce l'output testuale.
    
    Requisiti:
    - output deterministico
    - nessun parsing qui (solo testo)
    """

    client = get_client()

    response = client.chat.completions.create(
        model="gpt-4.1-mini",  # modello leggero e stabile
        temperature=0,         # determinismo massimo
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("Risposta vuota dal modello")

    return content.strip()