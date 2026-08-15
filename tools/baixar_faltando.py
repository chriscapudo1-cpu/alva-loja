"""Tenta de novo as fotos que falharam, com várias buscas."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from baixar_fotos_reais import OUT, is_jpeg, pull_jpg, yandex_hits

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "products.json"


def queries_for(item: dict) -> list[str]:
    name = item["name"]
    search = item.get("search") or ""
    return [
        search,
        f"{search} aliexpress",
        name,
        f"{name} produto",
        f"{search} product",
    ]


def grab(item: dict) -> bool:
    dest = OUT / f"{item['id']}.jpg"
    if dest.exists() and dest.stat().st_size > 4000:
        item["image"] = f"assets/img/ali/{item['id']}.jpg"
        return True
    seen: set[str] = set()
    for query in queries_for(item):
        query = (query or "").strip()
        if not query or query in seen:
            continue
        seen.add(query)
        print("try", item["id"], query, flush=True)
        try:
            imgs, _ = yandex_hits(query)
        except Exception as exc:
            print("  search fail", exc)
            continue
        for url in imgs[:10]:
            data = pull_jpg(url)
            if data and is_jpeg(data):
                dest.write_bytes(data)
                item["image"] = f"assets/img/ali/{item['id']}.jpg"
                print("  ok", dest.stat().st_size)
                return True
    print("  FAIL", item["id"])
    return False


def main() -> None:
    products = json.loads(SRC.read_text(encoding="utf-8"))
    ok = 0
    for item in products:
        own = OUT / f"{item['id']}.jpg"
        if own.exists() and own.stat().st_size > 4000:
            item["image"] = f"assets/img/ali/{item['id']}.jpg"
            ok += 1
            continue
        if grab(item):
            ok += 1
    SRC.write_text(json.dumps(products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    miss = [i["id"] for i in products if not (OUT / f"{i['id']}.jpg").exists()]
    print("own", ok, "still missing", miss)


if __name__ == "__main__":
    main()
