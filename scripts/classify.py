"""
Classifica candidatos de noticia via API da Claude (Haiku): descarta
irrelevantes e extrai emissor / tipo de evento / severidade / resumo.
"""
import json
import os

import requests

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-haiku-4-5-20251001"
BATCH_SIZE = 12

SYSTEM_PROMPT = """Voce e um analista de credito privado brasileiro. Voce recebe uma lista de \
manchetes de noticia (titulo + fonte + data) candidatas a eventos de estresse no mercado de \
credito privado (recuperacao judicial, calote, rebaixamento de rating, renegociacao de divida, \
covenant, fraude contabil, etc).

Para cada item da lista, avalie se e REALMENTE relevante para um analista de renda fixa de uma \
fundacao de previdencia mapear risco de credito -- descarte noticias genericas, editoriais, \
noticias sobre pessoas fisicas sem relacao com credito corporativo, ou mencoes superficiais sem \
um evento de credito concreto de uma empresa/emissor.

Responda SOMENTE com um array JSON, sem markdown, sem texto antes ou depois, no formato:
[
  {
    "index": 0,
    "relevante": true,
    "emissor": "Nome da empresa/emissor, ou null se nao identificavel",
    "tipo_evento": "recuperação judicial | recuperação extrajudicial | rebaixamento de rating | calote | renegociação de dívida | covenant | fraude contábil | outro",
    "severidade": "baixa | média | alta",
    "resumo": "resumo objetivo de 1 a 2 frases, em portugues"
  }
]
Se relevante for false, ainda inclua o indice, mas pode deixar os demais campos como null."""


def classify_batch(items, api_key):
    numbered = [
        {"index": i, "title": it["title"], "source": it["source"], "pub_date": it["pub_date"]}
        for i, it in enumerate(items)
    ]
    user_content = "Classifique estes candidatos:\n\n" + json.dumps(numbered, ensure_ascii=False, indent=2)

    resp = requests.post(
        API_URL,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": MODEL,
            "max_tokens": 2000,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_content}],
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    text_blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
    raw = "".join(text_blocks).strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        print("[classify] resposta nao-JSON, ignorando lote:\n", raw[:500])
        return []
    return parsed


def classify_all(items, api_key=None):
    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY nao configurada")

    results = []
    for start in range(0, len(items), BATCH_SIZE):
        batch = items[start : start + BATCH_SIZE]
        classified = classify_batch(batch, api_key)
        for c in classified:
            idx = c.get("index")
            if idx is None or idx >= len(batch):
                continue
            if not c.get("relevante"):
                continue
            base = batch[idx]
            results.append(
                {
                    **base,
                    "emissor": c.get("emissor"),
                    "tipo_evento": c.get("tipo_evento"),
                    "severidade": c.get("severidade"),
                    "resumo": c.get("resumo"),
                }
            )
    return results


if __name__ == "__main__":
    import sys

    with open(sys.argv[1], encoding="utf-8") as f:
        candidates = json.load(f)
    out = classify_all(candidates)
    print(json.dumps(out, ensure_ascii=False, indent=2))
