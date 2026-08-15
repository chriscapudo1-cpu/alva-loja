"""Testa formatos de preferência no Mercado Pago. Não imprime o token."""
import json
import os
import uuid
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if raw.startswith("MP_ACCESS_TOKEN="):
        os.environ["MP_ACCESS_TOKEN"] = raw.split("=", 1)[1].strip()

TOKEN = os.environ.get("MP_ACCESS_TOKEN", "")
ITEM = {
    "title": "Teste ALVA",
    "quantity": 1,
    "currency_id": "BRL",
    "unit_price": 10.0,
}


def post(name: str, payload: dict) -> None:
    req = Request(
        "https://api.mercadopago.com/checkout/preferences",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "X-Idempotency-Key": str(uuid.uuid4()),
        },
    )
    try:
        with urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        print("OK", name, "id=", data.get("id"), "url=", bool(data.get("init_point")))
    except HTTPError as exc:
        print("FAIL", name, exc.read().decode("utf-8", "replace")[:280])


cases = [
    ("items only", {"items": [ITEM]}),
    (
        "back_urls https + auto",
        {
            "items": [ITEM],
            "back_urls": {
                "success": "https://www.mercadopago.com.br/",
                "pending": "https://www.mercadopago.com.br/",
                "failure": "https://www.mercadopago.com.br/",
            },
            "auto_return": "approved",
        },
    ),
    (
        "back_url object + auto",
        {
            "items": [ITEM],
            "back_url": {
                "success": "https://www.mercadopago.com.br/",
                "pending": "https://www.mercadopago.com.br/",
                "failure": "https://www.mercadopago.com.br/",
            },
            "auto_return": "approved",
        },
    ),
    (
        "back_url string + auto",
        {
            "items": [ITEM],
            "back_url": "https://www.mercadopago.com.br/",
            "auto_return": "approved",
        },
    ),
    (
        "both back + auto",
        {
            "items": [ITEM],
            "back_url": {
                "success": "https://www.mercadopago.com.br/",
                "pending": "https://www.mercadopago.com.br/",
                "failure": "https://www.mercadopago.com.br/",
            },
            "back_urls": {
                "success": "https://www.mercadopago.com.br/",
                "pending": "https://www.mercadopago.com.br/",
                "failure": "https://www.mercadopago.com.br/",
            },
            "auto_return": "approved",
        },
    ),
    (
        "google back_urls + auto",
        {
            "items": [ITEM],
            "back_urls": {
                "success": "https://www.google.com/",
                "pending": "https://www.google.com/",
                "failure": "https://www.google.com/",
            },
            "auto_return": "approved",
        },
    ),
    (
        "no auto only back_urls",
        {
            "items": [ITEM],
            "back_urls": {
                "success": "https://www.mercadopago.com.br/",
                "pending": "https://www.mercadopago.com.br/",
                "failure": "https://www.mercadopago.com.br/",
            },
        },
    ),
]

for name, payload in cases:
    post(name, payload)
