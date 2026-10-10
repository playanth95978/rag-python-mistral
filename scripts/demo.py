"""Exécuter après avoir démarré uvicorn : uv run python scripts/demo.py."""

import httpx

with httpx.Client(base_url="http://127.0.0.1:8000/api/v1/", timeout=120) as client:
    response = client.post(
        "documents",
        json={
            "title": "Offre développeur IA Python",
            "text": "Nous recrutons un développeur Python. Compétences : FastAPI, API Mistral, embeddings et retrieval pour construire un RAG. Le KV cache accélère la génération en réutilisant les clés et valeurs de l’attention des tokens précédents. Télétravail : trois jours par semaine. Expérience : deux ans.",
        },
    )
    response.raise_for_status()
    print("Indexation :", response.json())
    for _ in range(2):
        response = client.post(
            "ask",
            json={
                "question": "Quelles compétences sont demandées et combien de jours de télétravail sont proposés ?"
            },
        )
        response.raise_for_status()
        print(response.json())
