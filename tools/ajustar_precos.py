"""Acima de R$ 150: lucro 30% sobre a venda. Demais: 50% (2x o custo)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "products.json"


def price_for(cost: float) -> float:
    doubled = cost * 2
    if doubled > 150:
        return round(cost / 0.70, 2)
    return round(doubled, 2)


def main() -> None:
    products = json.loads(SRC.read_text(encoding="utf-8"))
    changed = 0
    for item in products:
        cost = float(item.get("cost") or 0)
        old = float(item.get("price") or 0)
        new = price_for(cost)
        if abs(new - old) > 0.009:
            item["price"] = new
            changed += 1
        else:
            item["price"] = new
    SRC.write_text(json.dumps(products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"reprecificados: {changed}")


if __name__ == "__main__":
    main()
