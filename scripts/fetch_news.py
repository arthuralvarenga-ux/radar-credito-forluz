"""
Busca noticias no Google News RSS para uma lista de palavras-chave de
estresse no mercado de credito privado brasileiro. Nao usa nenhuma API key
(o Google News RSS e publico).
"""
import time
import urllib.parse
import xml.etree.ElementTree as ET

import requests

KEYWORDS = [
    "recuperação judicial",
    "recuperação extrajudicial",
    "calote de dívida",
    "default de debênture",
    "rebaixamento de rating",
    "renegociação de dívida",
    "covenant financeiro",
    "waiver de covenant",
    "fato relevante CVM",
    "inadimplência corporativa",
    "fraude contábil empresa",
    "quebra de covenant",
]

RSS_BASE = "https://news.google.com/rss/search"
LOOKBACK_DAYS = 8  # janela levemente maior que 7 dias pra nao perder nada na virada da semana


def build_url(keyword: str) -> str:
    query = f'"{keyword}" quando:{LOOKBACK_DAYS}d'
    params = {
        "q": query,
        "hl": "pt-BR",
        "gl": "BR",
        "ceid": "BR:pt-BR",
    }
    return f"{RSS_BASE}?{urllib.parse.urlencode(params)}"


def fetch_keyword(keyword: str, timeout: int = 15):
    url = build_url(keyword)
    resp = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    items = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        source_el = item.find("source")
        source = source_el.text.strip() if source_el is not None and source_el.text else ""
        if not link:
            continue
        items.append(
            {
                "keyword": keyword,
                "title": title,
                "link": link,
                "pub_date": pub_date,
                "source": source,
            }
        )
    return items


def fetch_all():
    all_items = []
    for kw in KEYWORDS:
        try:
            items = fetch_keyword(kw)
            all_items.extend(items)
            print(f"[fetch_news] '{kw}': {len(items)} resultado(s)")
        except Exception as exc:  # noqa: BLE001 - queremos seguir mesmo se uma keyword falhar
            print(f"[fetch_news] falha ao buscar '{kw}': {exc}")
        time.sleep(1)  # gentileza com o servico do Google

    # dedupe por link
    seen = set()
    deduped = []
    for it in all_items:
        if it["link"] in seen:
            continue
        seen.add(it["link"])
        deduped.append(it)
    return deduped


if __name__ == "__main__":
    import json

    result = fetch_all()
    print(json.dumps(result, ensure_ascii=False, indent=2))
