"""Liga no catálogo qualquer foto já baixada em assets/img/ali/."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALI = ROOT / "assets" / "img" / "ali"
products = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))
ok = 0
for item in products:
    dest = ALI / f"{item['id']}.jpg"
    dest_jpeg = ALI / f"{item['id']}.jpeg"
    file = dest if dest.exists() else dest_jpeg if dest_jpeg.exists() else None
    if not file or file.stat().st_size < 4000:
        continue
    item["image"] = f"assets/img/ali/{file.name}"
    ok += 1

(ROOT / "data" / "products.json").write_text(
    json.dumps(products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
try:
    with (ROOT / "data" / "fornecedores.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow(
            ["id", "categoria", "produto", "custo", "venda", "aliexpress", "loja"]
        )
        for item in products:
            writer.writerow(
                [
                    item["id"],
                    item["tag"],
                    item["name"],
                    f"{item['cost']:.2f}".replace(".", ","),
                    f"{item['price']:.2f}".replace(".", ","),
                    item.get("supplierUrl", ""),
                    "http://127.0.0.1:5173/produto.html?id=" + item["id"],
                ]
            )
except OSError as exc:
    print("csv skip", exc)
print("applied", ok, "of", len(products))
