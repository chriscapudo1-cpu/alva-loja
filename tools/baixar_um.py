"""Tenta de novo um produto que falhou."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from baixar_fotos_reais import OUT, is_jpeg, pull_jpg, yandex_hits

ROOT = Path(__file__).resolve().parents[1]
pid = sys.argv[1] if len(sys.argv) > 1 else "beleza-107"
queries = sys.argv[2:] or ["jade roller gua sha", "gua sha face roller", "jade facial roller"]

products = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))
item = next(x for x in products if x["id"] == pid)
dest = OUT / f"{pid}.jpg"

for query in queries:
    print("try", query, flush=True)
    try:
        imgs, _ = yandex_hits(query)
    except Exception as exc:
        print("  search fail", exc)
        continue
    for img in imgs:
        data = pull_jpg(img)
        if data and is_jpeg(data):
            dest.write_bytes(data)
            item["image"] = f"assets/img/ali/{pid}.jpg"
            (ROOT / "data" / "products.json").write_text(
                json.dumps(products, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print("ok", dest.stat().st_size, img[-60:])
            raise SystemExit(0)
print("FAIL")
raise SystemExit(1)
