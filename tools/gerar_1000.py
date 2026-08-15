"""Expande o catálogo atual (200) para 1000 produtos, reusando fotos locais."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "products.json"

SUFFIXES = [
    (" Pro", " pro", 1.22),
    (" Mini", " mini", 0.76),
    (" Kit 2", " 2 pack", 1.65),
    (" Plus", " plus", 1.38),
]

NEXT_ID = {
    "Tech": 21,
    "Casa": 41,
    "Pet": 61,
    "Moda": 81,
    "Carro": 101,
    "Beleza": 121,
    "Esporte": 141,
    "Bebê": 161,
    "Escritório": 181,
    "Cozinha": 201,
}

PREFIX = {
    "Tech": "tech",
    "Casa": "casa",
    "Pet": "pet",
    "Moda": "moda",
    "Carro": "carro",
    "Beleza": "beleza",
    "Esporte": "esporte",
    "Bebê": "bebe",
    "Escritório": "escritorio",
    "Cozinha": "cozinha",
}


def main() -> None:
    base = json.loads(SRC.read_text(encoding="utf-8"))
    by_cat: dict[str, list[dict]] = {}
    for item in base:
        by_cat.setdefault(item["tag"], []).append(item)

    extra: list[dict] = []
    for cat, items in by_cat.items():
        n = NEXT_ID[cat]
        prefix = PREFIX[cat]
        for item in items:
            for suffix, query_extra, factor in SUFFIXES:
                cost = round(float(item["cost"]) * factor, 2)
                extra.append(
                    {
                        "id": f"{prefix}-{n:03d}",
                        "name": f"{item['name']}{suffix}",
                        "cost": cost,
                        "price": round(cost * 2, 2),
                        "image": item["image"],
                        "tag": cat,
                        "blurb": f"{cat} · envio após a confirmação do pagamento.",
                        "stock": 30 + (n % 40),
                        "supplier": "AliExpress",
                        "supplierUrl": (
                            "https://pt.aliexpress.com/w/wholesale-"
                            f"{quote_plus((item.get('search') or item['name']) + query_extra)}.html"
                        ),
                        "search": f"{item.get('search') or item['name']}{query_extra}",
                    }
                )
                n += 1

    products = base + extra
    assert len(products) == 1000, len(products)
    ids = [p["id"] for p in products]
    assert len(ids) == len(set(ids))

    SRC.write_text(json.dumps(products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rows = []
    for item in products:
        rows.append(
            {
                "id": item["id"],
                "categoria": item["tag"],
                "produto": item["name"],
                "custo_brl": f"{item['cost']:.2f}".replace(".", ","),
                "venda_brl": f"{item['price']:.2f}".replace(".", ","),
                "aliexpress": item.get("supplierUrl") or "",
                "loja": f"https://alvaloja.store/produto.html?id={item['id']}",
            }
        )
    csv_path = ROOT / "data" / "fornecedores.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    print(f"gerados {len(products)} produtos")


if __name__ == "__main__":
    main()
