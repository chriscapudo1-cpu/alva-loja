"""Liga fotos baixadas e tira AliExpress do texto público."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALI = ROOT / "assets" / "img" / "ali"
products = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))
photos = 0
for item in products:
    dest = ALI / f"{item['id']}.jpg"
    if dest.exists() and dest.stat().st_size > 4000:
        item["image"] = f"assets/img/ali/{item['id']}.jpg"
        photos += 1
    item["blurb"] = f"{item['tag']} · envio após a confirmação do pagamento."

(ROOT / "data" / "products.json").write_text(
    json.dumps(products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print("photos", photos, "of", len(products))
