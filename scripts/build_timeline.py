"""
Funde novos eventos classificados no historico acumulado (data/eventos.json)
e regenera a timeline em HTML (docs/index.html).
"""
import hashlib
import json
import os
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "eventos.json")
HTML_PATH = os.path.join(BASE_DIR, "docs", "index.html")
TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "timeline_template.html")


def _id_for(item):
    return hashlib.sha256(item["link"].encode("utf-8")).hexdigest()[:16]


def _parse_date(pub_date):
    try:
        return parsedate_to_datetime(pub_date).astimezone(timezone.utc).isoformat()
    except Exception:  # noqa: BLE001
        return datetime.now(timezone.utc).isoformat()


def load_existing():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def merge(existing, new_items):
    by_id = {e["id"]: e for e in existing}
    added = 0
    for item in new_items:
        eid = _id_for(item)
        if eid in by_id:
            continue
        by_id[eid] = {
            "id": eid,
            "titulo": item["title"],
            "link": item["link"],
            "fonte": item["source"],
            "data_publicacao": _parse_date(item["pub_date"]),
            "keyword_gatilho": item["keyword"],
            "emissor": item.get("emissor"),
            "tipo_evento": item.get("tipo_evento"),
            "severidade": item.get("severidade"),
            "resumo": item.get("resumo"),
            "capturado_em": datetime.now(timezone.utc).isoformat(),
        }
        added += 1
    merged = sorted(by_id.values(), key=lambda e: e["data_publicacao"], reverse=True)
    return merged, added


def save(events):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)


def render_html(events):
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = f.read()
    payload = json.dumps(events, ensure_ascii=False)
    html = template.replace("__EVENTOS_JSON__", payload)
    html = html.replace("__ATUALIZADO_EM__", datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC"))
    os.makedirs(os.path.dirname(HTML_PATH), exist_ok=True)
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)


def run(new_items):
    existing = load_existing()
    merged, added = merge(existing, new_items)
    save(merged)
    render_html(merged)
    print(f"[build_timeline] {added} evento(s) novo(s); total acumulado: {len(merged)}")
    return added


if __name__ == "__main__":
    import sys

    with open(sys.argv[1], encoding="utf-8") as f:
        new_items = json.load(f)
    run(new_items)
