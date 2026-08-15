"""Baixa uma foto real (AliExpress via Yandex) para cada produto extra."""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from baixar_fotos_reais import OUT, is_jpeg, pull_jpg, yandex_hits

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "products.json"
WORKERS = 5


def needs_photo(item: dict) -> bool:
    dest = OUT / f"{item['id']}.jpg"
    return not (dest.exists() and dest.stat().st_size > 4000)


def one(item: dict) -> tuple[str, bool, str]:
    dest = OUT / f"{item['id']}.jpg"
    query = item.get("search") or item["name"]
    try:
        imgs, _ = yandex_hits(query)
    except Exception as exc:
        return item["id"], False, str(exc)
    for url in imgs[:8]:
        data = pull_jpg(url)
        if data and is_jpeg(data):
            dest.write_bytes(data)
            return item["id"], True, url
    return item["id"], False, "sem jpeg"


def main() -> None:
    products = json.loads(SRC.read_text(encoding="utf-8"))
    todo = [item for item in products if needs_photo(item)]
    print(f"faltam {len(todo)} fotos", flush=True)
    ok = 0
    fail = 0
    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futs = {pool.submit(one, item): item for item in todo}
        for fut in as_completed(futs):
            pid, good, info = fut.result()
            done += 1
            if good:
                ok += 1
                for item in products:
                    if item["id"] == pid:
                        item["image"] = f"assets/img/ali/{pid}.jpg"
                        break
                print(f"ok {done}/{len(todo)} {pid}", flush=True)
            else:
                fail += 1
                print(f"fail {done}/{len(todo)} {pid} {info}", flush=True)
            if done % 25 == 0:
                SRC.write_text(
                    json.dumps(products, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
            time.sleep(0.05)
    SRC.write_text(json.dumps(products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("done ok", ok, "fail", fail)


if __name__ == "__main__":
    main()
