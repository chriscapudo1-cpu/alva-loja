"""Baixa a foto real do primeiro anúncio AliExpress de cada produto."""

from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "img" / "ali"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def fetch(url: str, timeout: int = 40) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def first_product_image(markdown: str) -> tuple[str, str]:
    imgs = re.findall(
        r"!\[([^\]]*)\]\((https://ae-pic-a1\.aliexpress-media\.com/kf/[^)]+\.jpg[^)]*)\)",
        markdown,
    )
    item = ""
    ids = re.findall(r"aliexpress\.com/item/(\d+)\.html", markdown)
    if not ids:
        ids = re.findall(r"x_object_id%3A(\d+)", markdown)
    if not ids:
        ids = re.findall(r"productIds=(\d+)", markdown)
    if ids:
        item = f"https://pt.aliexpress.com/item/{ids[0]}.html"
    for alt, url in imgs:
        if any(bad in url for bad in ("27x27", "48x48", "45x60", "154x64", "702x72", "60x60")):
            continue
        if "480x480" in url or url.lower().endswith(".jpg") or ".jpg_" in url:
            clean = url.split("_.avif")[0]
            clean = re.sub(r"_\d+x\d+q\d+\.jpg$", ".jpg", clean)
            if clean.endswith(".jpg") or ".jpg" in clean:
                # prefer original file
                m = re.search(r"(https://ae-pic-a1\.aliexpress-media\.com/kf/[A-Za-z0-9]+\.jpg)", clean)
                if m:
                    return m.group(1), item
                return clean, item
    return "", item


def download_jpg(url: str, dest: Path) -> bool:
    try:
        data = fetch(url, timeout=25)
    except Exception:
        # fallback alicdn
        alt = url.replace("ae-pic-a1.aliexpress-media.com", "ae01.alicdn.com")
        try:
            data = fetch(alt, timeout=25)
        except Exception:
            return False
    if len(data) < 4000:
        return False
    if data[:3] != b"\xff\xd8\xff" and data[:8] != b"\x89PNG\r\n\x1a\n":
        # still save if reasonably large jpeg-like
        if b"JFIF" not in data[:32] and b"WEBP" not in data[:16]:
            return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return True


def main() -> None:
    products = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))
    cache: dict[str, tuple[str, str]] = {}
    ok = 0
    fail = 0
    for i, product in enumerate(products, 1):
        dest = OUT / f"{product['id']}.jpg"
        query = product.get("search") or product["name"]
        if dest.exists() and dest.stat().st_size > 4000:
            product["image"] = f"assets/img/ali/{product['id']}.jpg"
            ok += 1
            print(f"[{i}/200] skip {product['id']}")
            continue
        if query not in cache:
            page = f"https://www.aliexpress.com/w/wholesale-{urllib.parse.quote(query)}.html"
            jina = "https://r.jina.ai/" + page
            try:
                md = fetch(jina, timeout=50).decode("utf-8", "replace")
                cache[query] = first_product_image(md)
            except Exception as exc:
                print(f"[{i}/200] jina fail {product['id']}: {exc}")
                cache[query] = ("", "")
            time.sleep(0.7)
        img_url, item_url = cache[query]
        if item_url:
            product["supplierUrl"] = item_url
        if img_url and download_jpg(img_url, dest):
            product["image"] = f"assets/img/ali/{product['id']}.jpg"
            ok += 1
            print(f"[{i}/200] ok {product['name'][:40]}")
        else:
            fail += 1
            print(f"[{i}/200] no-img {product['id']}")
        if i % 10 == 0:
            (ROOT / "data" / "products.json").write_text(
                json.dumps(products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
    (ROOT / "data" / "products.json").write_text(
        json.dumps(products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    # refresh csv supplier urls
    print(f"done ok={ok} fail={fail}")


if __name__ == "__main__":
    main()
