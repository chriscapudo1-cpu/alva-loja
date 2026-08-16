"""Preenche galerias oficiais em ciclo até acabar ou o tempo esgotar."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from galeria_oficial import SRC, already_good, fill_one

MAX_HOURS = 6.5
PAUSE_WHEN_BLOCKED = 180


def snapshot(products: list[dict]) -> dict[int, int]:
    sizes: dict[int, int] = {}
    for item in products:
        n = len(item.get("images") or [])
        sizes[n] = sizes.get(n, 0) + 1
    return dict(sorted(sizes.items()))


def main() -> None:
    started = time.time()
    pass_no = 0
    while time.time() - started < MAX_HOURS * 3600:
        pass_no += 1
        products = json.loads(SRC.read_text(encoding="utf-8"))
        todo = [item for item in products if not already_good(item)]
        print(f"pass {pass_no} leftover {len(todo)} sizes {snapshot(products)}", flush=True)
        if not todo:
            print("catalogo completo", flush=True)
            break
        ok = 0
        fail = 0
        blocked = 0
        for index, item in enumerate(todo, 1):
            if time.time() - started > MAX_HOURS * 3600:
                break
            try:
                pid, count, info = fill_one(item)
            except Exception as exc:
                pid, count, info = item["id"], 0, str(exc)
            if count >= 2:
                ok += 1
                print(f"ok {index}/{len(todo)} {pid} +{count} {info}", flush=True)
            else:
                fail += 1
                print(f"fail {index}/{len(todo)} {pid} {info}", flush=True)
                if "galeria-curta" in str(info) or "punish" in str(info).lower():
                    blocked += 1
            if index % 4 == 0:
                SRC.write_text(json.dumps(products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            time.sleep(2.2)
            if blocked >= 8 and ok == 0:
                print("aliexpress bloqueada; pauso", flush=True)
                break
        SRC.write_text(json.dumps(products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"pass {pass_no} done ok {ok} fail {fail} sizes {snapshot(products)}", flush=True)
        if not [item for item in products if not already_good(item)]:
            print("catalogo completo", flush=True)
            break
        time.sleep(PAUSE_WHEN_BLOCKED)
    print("encerrei sizes", snapshot(json.loads(SRC.read_text(encoding="utf-8"))), flush=True)


if __name__ == "__main__":
    main()
