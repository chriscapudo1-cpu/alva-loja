"""Baixa 2 fotos extras de cada produto (mesma busca, outras imagens)."""
from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from baixar_fotos_reais import OUT, is_jpeg, pull_jpg, yandex_hits

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "products.json"
WORKERS = 5


def hashes_of(pid: str) -> set[int]:
    seen: set[int] = set()
    for suffix in ("", "-2", "-3"):
        path = OUT / f"{pid}{suffix}.jpg"
        if path.exists() and path.stat().st_size > 4000:
            seen.add(hash(path.read_bytes()[:800]))
    return seen


def fill(item: dict) -> tuple[str, int]:
    pid = item["id"]
    need = [s for s in ("-2", "-3") if not (OUT / f"{pid}{s}.jpg").exists()]
    if not need:
        return pid, 0
    query = item.get("search") or item["name"]
    try:
        imgs, _ = yandex_hits(query)
    except Exception:
        return pid, 0
    known = hashes_of(pid)
    saved = 0
    for url in imgs:
        if saved >= len(need):
            break
        data = pull_jpg(url)
        if not data or not is_jpeg(data):
            continue
        digest = hash(data[:800])
        if digest in known:
            continue
        dest = OUT / f"{pid}{need[saved]}.jpg"
        dest.write_bytes(data)
        known.add(digest)
        saved += 1
    return pid, saved


def main() -> None:
    products = json.loads(SRC.read_text(encoding="utf-8"))
    todo = [
        item
        for item in products
        if not (OUT / f"{item['id']}-2.jpg").exists() or not (OUT / f"{item['id']}-3.jpg").exists()
    ]
    print(f"galeria: {len(todo)} produtos para completar", flush=True)
    got = 0
    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futs = {pool.submit(fill, item): item for item in todo}
        for fut in as_completed(futs):
            pid, n = fut.result()
            done += 1
            got += n
            if done % 25 == 0 or n:
                print(f"{done}/{len(todo)} {pid} +{n}", flush=True)
    print("novas fotos", got)


if __name__ == "__main__":
    main()
