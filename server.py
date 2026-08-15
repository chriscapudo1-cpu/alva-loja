#!/usr/bin/env python3
"""ALVA — loja + Mercado Pago + painel de pedidos."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DB_PATH = DATA / "orders.db"
PRODUCTS_PATH = DATA / "products.json"


def load_env() -> None:
    path = ROOT / ".env"
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()

PORT = int(os.environ.get("PORT", "5173"))
HOST = os.environ.get("HOST", "0.0.0.0")
PUBLIC_URL = os.environ.get("PUBLIC_URL", f"http://127.0.0.1:{PORT}").rstrip("/")
MP_ACCESS_TOKEN = os.environ.get("MP_ACCESS_TOKEN", "").strip()
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "lume2026")
SHIP_FREE_FROM = 200.0
SHIP_PRICE = 18.9


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_products() -> list[dict]:
    return json.loads(PRODUCTS_PATH.read_text(encoding="utf-8"))


def product_map() -> dict[str, dict]:
    return {item["id"]: item for item in load_products()}


def db() -> sqlite3.Connection:
    DATA.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            status TEXT NOT NULL,
            customer_json TEXT NOT NULL,
            items_json TEXT NOT NULL,
            subtotal REAL NOT NULL,
            shipping REAL NOT NULL,
            total REAL NOT NULL,
            mp_preference_id TEXT,
            mp_payment_id TEXT,
            mp_status TEXT,
            notes TEXT
        )
        """
    )
    conn.commit()
    return conn


def row_to_order(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "createdAt": row["created_at"],
        "status": row["status"],
        "customer": json.loads(row["customer_json"]),
        "items": json.loads(row["items_json"]),
        "subtotal": row["subtotal"],
        "shipping": row["shipping"],
        "total": row["total"],
        "mpPreferenceId": row["mp_preference_id"],
        "mpPaymentId": row["mp_payment_id"],
        "mpStatus": row["mp_status"],
        "notes": row["notes"],
    }


def admin_token() -> str:
    return hmac.new(
        ADMIN_PASSWORD.encode("utf-8"),
        b"lume-admin-session",
        hashlib.sha256,
    ).hexdigest()


def is_admin(handler: "Handler") -> bool:
    header = handler.headers.get("X-Admin-Token", "")
    return hmac.compare_digest(header, admin_token())


def json_body(handler: "Handler") -> dict:
    length = int(handler.headers.get("Content-Length") or 0)
    raw = handler.rfile.read(length) if length else b"{}"
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


def build_order_items(cart: list) -> tuple[list[dict], float]:
    catalog = product_map()
    items: list[dict] = []
    subtotal = 0.0
    if not isinstance(cart, list) or not cart:
        raise ValueError("A sacola está vazia.")
    for entry in cart:
        product_id = str(entry.get("id") or "")
        qty = int(entry.get("qty") or 0)
        product = catalog.get(product_id)
        if not product:
            raise ValueError("Um item da sacola não existe mais.")
        if qty < 1 or qty > 20:
            raise ValueError("Quantidade inválida.")
        if qty > int(product.get("stock") or 0):
            raise ValueError(f"{product['name']} não tem essa quantidade.")
        line = {
            "id": product["id"],
            "name": product["name"],
            "price": float(product["price"]),
            "cost": float(product.get("cost") or 0),
            "qty": qty,
            "image": product["image"],
            "supplierUrl": product.get("supplierUrl") or "",
        }
        items.append(line)
        subtotal += line["price"] * qty
    return items, round(subtotal, 2)


def shipping_for(subtotal: float) -> float:
    return 0.0 if subtotal >= SHIP_FREE_FROM else SHIP_PRICE


def write_env_key(key: str, value: str) -> None:
    path = ROOT / ".env"
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    found = False
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"{key}=") or stripped.startswith(f"{key} ="):
            out.append(f"{key}={value}")
            found = True
        else:
            out.append(line)
    if not found:
        if out and out[-1] != "":
            out.append("")
        out.append(f"{key}={value}")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    os.environ[key] = value


def set_mp_token(token: str) -> None:
    global MP_ACCESS_TOKEN
    MP_ACCESS_TOKEN = token.strip()
    write_env_key("MP_ACCESS_TOKEN", MP_ACCESS_TOKEN)


def probe_mp(token: str) -> dict:
    req = Request(
        "https://api.mercadopago.com/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError("Token inválido. Confira se copiou o Access Token de produção.") from exc
    except URLError as exc:
        raise RuntimeError(f"Não foi possível falar com o Mercado Pago: {exc.reason}") from exc
    return {
        "id": data.get("id"),
        "nickname": data.get("nickname") or data.get("first_name") or "",
        "email": data.get("email") or "",
        "site": data.get("site_id") or "",
    }


def payment_status() -> dict:
    info = {
        "mercadoPago": bool(MP_ACCESS_TOKEN),
        "tokenTail": MP_ACCESS_TOKEN[-4:] if len(MP_ACCESS_TOKEN) >= 4 else "",
        "publicUrl": PUBLIC_URL,
        "freeFrom": SHIP_FREE_FROM,
        "shipPrice": SHIP_PRICE,
    }
    if MP_ACCESS_TOKEN:
        try:
            info["account"] = probe_mp(MP_ACCESS_TOKEN)
        except Exception as exc:
            info["accountError"] = str(exc)
    return info


def mp_request(method: str, path: str, payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(
        f"https://api.mercadopago.com{path}",
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {MP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
            "X-Idempotency-Key": str(uuid.uuid4()),
        },
    )
    try:
        with urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Mercado Pago ({exc.code}): {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Não foi possível falar com o Mercado Pago: {exc.reason}") from exc


def create_preference(order_id: str, items: list[dict], shipping: float, customer: dict) -> dict:
    mp_items = [
        {
            "id": item["id"],
            "title": item["name"],
            "quantity": item["qty"],
            "currency_id": "BRL",
            "unit_price": float(item["price"]),
        }
        for item in items
    ]
    if shipping > 0:
        mp_items.append(
            {
                "id": "frete",
                "title": "Frete",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": float(shipping),
            }
        )
    parsed = urlparse(PUBLIC_URL)
    host = (parsed.hostname or "").lower()
    public = parsed.scheme == "https" and host not in {
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
    }
    # MP trata localhost como URL vazia e recusa auto_return.
    return_base = PUBLIC_URL.rstrip("/") if public else "https://www.mercadopago.com.br"
    success = f"{return_base}/pedido.html?status=success&order={order_id}" if public else f"{return_base}/"
    failure = f"{return_base}/pedido.html?status=failure&order={order_id}" if public else f"{return_base}/"
    pending = f"{return_base}/pedido.html?status=pending&order={order_id}" if public else f"{return_base}/"
    back = {"success": success, "pending": pending, "failure": failure}
    payload = {
        "items": mp_items,
        "payer": {
            "name": customer.get("name", ""),
            "email": customer.get("email", ""),
        },
        "external_reference": order_id,
        "statement_descriptor": "ALVA LOJA",
        "back_urls": back,
        "auto_return": "approved",
        "metadata": {"order_id": order_id},
    }
    if public:
        payload["notification_url"] = f"{PUBLIC_URL}/api/webhook"
    return mp_request("POST", "/checkout/preferences", payload)


def apply_payment(order_id: str, payment_id: str, mp_status: str) -> None:
    mapping = {
        "approved": "pago",
        "authorized": "pago",
        "pending": "pendente",
        "in_process": "pendente",
        "in_mediation": "pendente",
        "rejected": "recusado",
        "cancelled": "cancelado",
        "refunded": "reembolsado",
        "charged_back": "estornado",
    }
    status = mapping.get(mp_status, "pendente")
    conn = db()
    conn.execute(
        """
        UPDATE orders
        SET status = ?, mp_payment_id = ?, mp_status = ?
        WHERE id = ?
        """,
        (status, str(payment_id), mp_status, order_id),
    )
    conn.commit()
    conn.close()


def sync_payment(payment_id: str) -> None:
    if not MP_ACCESS_TOKEN or not payment_id:
        return
    payment = mp_request("GET", f"/v1/payments/{payment_id}")
    order_id = (
        payment.get("external_reference")
        or (payment.get("metadata") or {}).get("order_id")
        or ""
    )
    if not order_id:
        return
    apply_payment(order_id, str(payment.get("id") or payment_id), str(payment.get("status") or ""))


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[{utc_now()}] {self.address_string()} {fmt % args}")

    def send_json(self, payload, status: int = 200) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(length) if length else b""

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/products":
            public = [
                {
                    "id": item["id"],
                    "name": item["name"],
                    "price": item["price"],
                    "image": item["image"],
                    "images": [item["image"]],
                    "tag": item["tag"],
                    "blurb": item["blurb"],
                    "description": item.get("description") or item.get("blurb") or "",
                    "stock": item["stock"],
                }
                for item in load_products()
            ]
            category = (parse_qs(parsed.query).get("cat") or [""])[0]
            if category:
                public = [item for item in public if item["tag"] == category]
            self.send_json({"products": public})
            return
        if parsed.path == "/api/categories":
            cats = []
            seen = set()
            for item in load_products():
                tag = item.get("tag") or ""
                if tag and tag not in seen:
                    seen.add(tag)
                    cats.append(tag)
            self.send_json({"categories": cats})
            return
        if parsed.path == "/api/admin/catalog":
            if not is_admin(self):
                self.send_json({"error": "Não autorizado."}, 401)
                return
            self.send_json({"products": load_products()})
            return
        if parsed.path == "/api/config":
            self.send_json(
                {
                    "mercadoPago": bool(MP_ACCESS_TOKEN),
                    "publicUrl": PUBLIC_URL,
                    "freeFrom": SHIP_FREE_FROM,
                    "shipPrice": SHIP_PRICE,
                }
            )
            return
        if parsed.path == "/api/admin/payment":
            if not is_admin(self):
                self.send_json({"error": "Não autorizado."}, 401)
                return
            self.send_json(payment_status())
            return
        if parsed.path == "/api/order":
            order_id = (parse_qs(parsed.query).get("id") or [""])[0]
            conn = db()
            row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
            conn.close()
            if not row:
                self.send_json({"error": "Pedido não encontrado."}, 404)
                return
            order = row_to_order(row)
            self.send_json(
                {
                    "order": {
                        "id": order["id"],
                        "status": order["status"],
                        "items": order["items"],
                        "subtotal": order["subtotal"],
                        "shipping": order["shipping"],
                        "total": order["total"],
                        "createdAt": order["createdAt"],
                    }
                }
            )
            return
        if parsed.path == "/api/admin/orders":
            if not is_admin(self):
                self.send_json({"error": "Não autorizado."}, 401)
                return
            conn = db()
            rows = conn.execute("SELECT * FROM orders ORDER BY created_at DESC").fetchall()
            conn.close()
            self.send_json({"orders": [row_to_order(row) for row in rows]})
            return
        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/checkout":
            try:
                payload = json.loads(self.read_body().decode("utf-8") or "{}")
                customer = payload.get("customer") or {}
                name = str(customer.get("name") or "").strip()
                email = str(customer.get("email") or "").strip()
                phone = str(customer.get("phone") or "").strip()
                address = str(customer.get("address") or "").strip()
                city = str(customer.get("city") or "").strip()
                cep = str(customer.get("cep") or "").strip()
                if not name or "@" not in email or not phone or not address or not city or not cep:
                    raise ValueError("Preencha nome, e-mail, telefone e endereço.")
                items, subtotal = build_order_items(payload.get("items") or [])
                shipping = shipping_for(subtotal)
                total = round(subtotal + shipping, 2)
                order_id = uuid.uuid4().hex[:10]
                status = "aguardando_pagamento" if MP_ACCESS_TOKEN else "reservado"
                preference_id = None
                checkout_url = f"/pedido.html?status=reserved&order={order_id}"
                if MP_ACCESS_TOKEN:
                    pref = create_preference(
                        order_id,
                        items,
                        shipping,
                        {"name": name, "email": email},
                    )
                    preference_id = pref.get("id")
                    checkout_url = pref.get("init_point") or pref.get("sandbox_init_point")
                    if not checkout_url:
                        raise RuntimeError("O Mercado Pago não devolveu o link de pagamento.")
                conn = db()
                conn.execute(
                    """
                    INSERT INTO orders (
                        id, created_at, status, customer_json, items_json,
                        subtotal, shipping, total, mp_preference_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        order_id,
                        utc_now(),
                        status,
                        json.dumps(
                            {
                                "name": name,
                                "email": email,
                                "phone": phone,
                                "address": address,
                                "city": city,
                                "cep": cep,
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(items, ensure_ascii=False),
                        subtotal,
                        shipping,
                        total,
                        preference_id,
                    ),
                )
                conn.commit()
                conn.close()
                self.send_json(
                    {
                        "orderId": order_id,
                        "checkoutUrl": checkout_url,
                        "mercadoPago": bool(MP_ACCESS_TOKEN),
                    }
                )
            except ValueError as exc:
                self.send_json({"error": str(exc)}, 400)
            except Exception as exc:
                self.send_json({"error": str(exc)}, 502)
            return

        if parsed.path == "/api/webhook":
            raw = self.read_body()
            query = parse_qs(parsed.query)
            payment_id = ""
            try:
                body = json.loads(raw.decode("utf-8") or "{}") if raw else {}
            except json.JSONDecodeError:
                body = {}
            payment_id = str(
                (body.get("data") or {}).get("id")
                or body.get("id")
                or (query.get("data.id") or [""])[0]
                or (query.get("id") or [""])[0]
            )
            topic = str(body.get("type") or body.get("topic") or (query.get("topic") or [""])[0])
            if topic in {"payment", "topic_payment", ""} and payment_id and payment_id != "123456":
                try:
                    sync_payment(payment_id)
                except Exception as exc:
                    print(f"webhook error: {exc}")
            self.send_json({"ok": True})
            return

        if parsed.path == "/api/order/sync":
            try:
                payload = json.loads(self.read_body().decode("utf-8") or "{}")
                order_id = str(payload.get("orderId") or "")
                payment_id = str(payload.get("paymentId") or "")
                status_hint = str(payload.get("status") or "")
                if payment_id and MP_ACCESS_TOKEN:
                    sync_payment(payment_id)
                elif order_id and status_hint in {"success", "approved"}:
                    apply_payment(order_id, payment_id or "", "approved")
                elif order_id and status_hint in {"failure", "rejected"}:
                    apply_payment(order_id, payment_id or "", "rejected")
                elif order_id and status_hint in {"pending"}:
                    apply_payment(order_id, payment_id or "", "pending")
                self.send_json({"ok": True})
            except Exception as exc:
                self.send_json({"error": str(exc)}, 400)
            return

        if parsed.path == "/api/admin/login":
            try:
                payload = json.loads(self.read_body().decode("utf-8") or "{}")
            except json.JSONDecodeError:
                payload = {}
            password = str(payload.get("password") or "")
            if not hmac.compare_digest(password, ADMIN_PASSWORD):
                self.send_json({"error": "Senha incorreta."}, 401)
                return
            self.send_json({"token": admin_token()})
            return

        if parsed.path == "/api/admin/payment":
            if not is_admin(self):
                self.send_json({"error": "Não autorizado."}, 401)
                return
            try:
                payload = json.loads(self.read_body().decode("utf-8") or "{}")
                token = str(payload.get("accessToken") or "").strip()
                if not token:
                    raise ValueError("Cole o Access Token do Mercado Pago.")
                account = probe_mp(token)
                set_mp_token(token)
                self.send_json({"ok": True, **payment_status(), "account": account})
            except ValueError as exc:
                self.send_json({"error": str(exc)}, 400)
            except Exception as exc:
                self.send_json({"error": str(exc)}, 400)
            return

        self.send_json({"error": "Não encontrado."}, 404)

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()


def main() -> None:
    db().close()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    mode = "Mercado Pago ligado" if MP_ACCESS_TOKEN else "modo reserva (sem token do Mercado Pago)"
    print(f"ALVA loja em http://127.0.0.1:{PORT}  — {mode}")
    print(f"Público: {PUBLIC_URL}")
    print(f"Pedidos: {PUBLIC_URL}/admin.html")
    server.serve_forever()


if __name__ == "__main__":
    main()
