"""Remove buscas genéricas e deixa só link de anúncio /item/."""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "products.json"
products = json.loads(SRC.read_text(encoding="utf-8"))
kept = 0
cleared = 0
for item in products:
    url = str(item.get("supplierUrl") or "")
    match = re.search(r"aliexpress\.com/item/(\d+)", url, re.I)
    if match:
        item["supplierUrl"] = f"https://pt.aliexpress.com/item/{match.group(1)}.html"
        kept += 1
    else:
        if url:
            cleared += 1
        item["supplierUrl"] = ""
SRC.write_text(json.dumps(products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
csv_path = ROOT / "data" / "fornecedores.csv"
with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.writer(handle, delimiter=";")
    writer.writerow(["id", "categoria", "produto", "custo_brl", "venda_brl", "aliexpress", "loja"])
    for item in products:
        writer.writerow(
            [
                item["id"],
                item["tag"],
                item["name"],
                f"{item['cost']:.2f}".replace(".", ","),
                f"{item['price']:.2f}".replace(".", ","),
                item.get("supplierUrl") or "",
                f"https://alvaloja.store/produto.html?id={item['id']}",
            ]
        )
print("kept", kept, "cleared", cleared)
