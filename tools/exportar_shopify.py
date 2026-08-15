"""Gera CSV de produtos no formato de importação da Shopify."""
import csv
import json
import re
from pathlib import Path
from unicodedata import normalize

ROOT = Path(__file__).resolve().parents[1]
products = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))


def handle(item: dict) -> str:
    text = normalize("NFKD", item["name"]).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return slug or item["id"]


fields = [
    "Handle",
    "Title",
    "Body (HTML)",
    "Vendor",
    "Product Category",
    "Type",
    "Tags",
    "Published",
    "Option1 Name",
    "Option1 Value",
    "Variant SKU",
    "Variant Grams",
    "Variant Inventory Tracker",
    "Variant Inventory Qty",
    "Variant Inventory Policy",
    "Variant Fulfillment Service",
    "Variant Price",
    "Variant Compare At Price",
    "Variant Requires Shipping",
    "Variant Taxable",
    "Gift Card",
    "SEO Title",
    "SEO Description",
    "Status",
]

out = ROOT / "data" / "shopify-produtos.csv"
with out.open("w", encoding="utf-8-sig", newline="") as handle_file:
    writer = csv.DictWriter(handle_file, fieldnames=fields)
    writer.writeheader()
    for item in products:
        slug = handle(item)
        writer.writerow(
            {
                "Handle": slug,
                "Title": item["name"],
                "Body (HTML)": f"<p>{item['blurb']}</p>",
                "Vendor": "ALVA",
                "Product Category": "",
                "Type": item["tag"],
                "Tags": item["tag"],
                "Published": "TRUE",
                "Option1 Name": "Title",
                "Option1 Value": "Default Title",
                "Variant SKU": item["id"],
                "Variant Grams": "300",
                "Variant Inventory Tracker": "shopify",
                "Variant Inventory Qty": item.get("stock", 20),
                "Variant Inventory Policy": "deny",
                "Variant Fulfillment Service": "manual",
                "Variant Price": f"{item['price']:.2f}",
                "Variant Compare At Price": "",
                "Variant Requires Shipping": "TRUE",
                "Variant Taxable": "FALSE",
                "Gift Card": "FALSE",
                "SEO Title": f"{item['name']} — ALVA",
                "SEO Description": item["blurb"],
                "Status": "active",
            }
        )

sup = ROOT / "data" / "shopify-fornecedores.csv"
with sup.open("w", encoding="utf-8-sig", newline="") as handle_file:
    writer = csv.writer(handle_file, delimiter=";")
    writer.writerow(
        ["sku", "handle", "produto", "categoria", "custo", "venda", "aliexpress", "foto_local"]
    )
    for item in products:
        writer.writerow(
            [
                item["id"],
                handle(item),
                item["name"],
                item["tag"],
                f"{item['cost']:.2f}".replace(".", ","),
                f"{item['price']:.2f}".replace(".", ","),
                item.get("supplierUrl", ""),
                item.get("image", ""),
            ]
        )

print(out.name, len(products))
print(sup.name)
