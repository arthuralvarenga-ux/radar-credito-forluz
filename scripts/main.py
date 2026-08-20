import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetch_news import fetch_all  # noqa: E402
from classify import classify_all  # noqa: E402
from build_timeline import run as build_timeline_run  # noqa: E402


def main():
    print("[main] buscando candidatos...")
    candidates = fetch_all()
    print(f"[main] {len(candidates)} candidato(s) encontrado(s) apos dedupe por link")

    if not candidates:
        print("[main] nenhum candidato, nada a classificar")
        build_timeline_run([])
        return

    print("[main] classificando via API Claude...")
    classified = classify_all(candidates)
    print(f"[main] {len(classified)} evento(s) considerado(s) relevante(s)")

    added = build_timeline_run(classified)
    print(f"[main] concluido. {added} evento(s) novo(s) adicionado(s) ao historico.")


if __name__ == "__main__":
    main()
