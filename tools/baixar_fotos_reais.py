"""Baixa a foto do anúncio AliExpress de cada produto (Yandex + página do item)."""
from __future__ import annotations

import csv
import json
import re
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "img" / "ali"
OUT.mkdir(parents=True, exist_ok=True)
CTX = ssl.create_default_context()
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
IMG_RE = re.compile(
    r"https://(?:ae-pic-a1\.aliexpress-media|ae01\.alicdn)\.com/kf/[A-Za-z0-9]+\.(?:jpg|jpeg|png)",
    re.I,
)
ITEM_RE = re.compile(r"https?://(?:[a-z]+\.)?aliexpress\.com/(?:item|i)/(\d+)", re.I)


def fetch(url: str, timeout: int = 18, accept: str = "text/html,*/*;q=0.8") -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": accept,
            "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as resp:
        return resp.read()


def unique(seq: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in seq:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def yandex_hits(query: str) -> tuple[list[str], list[str]]:
    url = "https://yandex.com/images/search?text=" + urllib.parse.quote(
        f"{query} aliexpress"
    )
    html = fetch(url).decode("utf-8", "replace")
    imgs = unique(IMG_RE.findall(html))
    items = unique(ITEM_RE.findall(html))
    return imgs, items


def item_hits(item_id: str) -> tuple[list[str], str]:
    link = f"https://pt.aliexpress.com/item/{item_id}.html"
    try:
        html = fetch(link).decode("utf-8", "replace")
    except Exception:
        return [], link
    return unique(IMG_RE.findall(html)), link


def is_jpeg(data: bytes) -> bool:
    return len(data) > 4000 and data[:3] == b"\xff\xd8\xff"


def pull_jpg(url: str) -> bytes | None:
    candidates = [url]
    if not url.endswith("_480x480.jpg"):
        candidates.append(url + "_480x480.jpg")
    alt = url.replace("ae-pic-a1.aliexpress-media.com", "ae01.alicdn.com")
    if alt != url:
        candidates.append(alt)
    for candidate in candidates:
        try:
            data = fetch(candidate, timeout=25, accept="image/jpeg")
            if is_jpeg(data):
                return data
        except Exception:
            continue
    return None


def write_csv(products: list[dict]) -> None:
    path = ROOT / "data" / "fornecedores.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
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


def main() -> None:
    products = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))
    ok = 0
    fail = 0
    used_imgs: set[str] = set()
    for item in products:
        dest = OUT / f"{item['id']}.jpg"
        if dest.exists() and is_jpeg(dest.read_bytes()):
            item["image"] = f"assets/img/ali/{item['id']}.jpg"
            ok += 1
            print("skip", item["id"])
            continue

        query = item.get("search") or item["name"]
        print("fetch", item["id"], query, flush=True)
        imgs: list[str] = []
        items: list[str] = []
        try:
            imgs, items = yandex_hits(query)
        except Exception as exc:
            print("  yandex fail", exc)

        chosen_img = ""
        chosen_item = items[0] if items else ""
        if chosen_item:
            extra, link = item_hits(chosen_item)
            item["supplierUrl"] = link
            if extra:
                imgs = extra + imgs

        data = None
        for img in imgs:
            if img in used_imgs:
                continue
            data = pull_jpg(img)
            if data:
                chosen_img = img
                break

        if not data:
            fail += 1
            print("  FAIL")
            time.sleep(1.2)
            continue

        dest.write_bytes(data)
        used_imgs.add(chosen_img)
        item["image"] = f"assets/img/ali/{item['id']}.jpg"
        if chosen_item and not item.get("supplierUrl", "").endswith(".html"):
            item["supplierUrl"] = f"https://pt.aliexpress.com/item/{chosen_item}.html"
        ok += 1
        print("  ok", dest.stat().st_size, chosen_img[-50:])
        if ok % 5 == 0:
            (ROOT / "data" / "products.json").write_text(
                json.dumps(products, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        time.sleep(0.8)

    (ROOT / "data" / "products.json").write_text(
        json.dumps(products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    try:
        write_csv(products)
    except OSError as exc:
        print("csv skip", exc)
    print("done ok", ok, "fail", fail)


if __name__ == "__main__":
    main()
