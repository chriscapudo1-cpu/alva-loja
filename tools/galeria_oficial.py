"""Baixa 3 fotos oficiais do MESMO anúncio AliExpress para cada produto."""
from __future__ import annotations

import io
import json
import re
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "products.json"
OUT = ROOT / "assets" / "img" / "ali"
OUT.mkdir(parents=True, exist_ok=True)
CTX = ssl.create_default_context()
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
ITEM_RE = re.compile(
    r"aliexpress\.(?:com|ru)/(?:item|i)/(\d{10,})",
    re.I,
)
IMG_RE = re.compile(
    r"https://(?:ae-pic-a1\.aliexpress-media|ae0\d\.alicdn)\.com/kf/[A-Za-z0-9]+\.(?:jpg|jpeg|png)",
    re.I,
)
ORIG_RE = re.compile(
    r'"origUrl":"(https://(?:ae-pic-a1\.aliexpress-media|ae0\d\.alicdn)\.com/kf/[^"]+)"',
    re.I,
)
PATH_RE = re.compile(r'"imagePathList"\s*:\s*(\[[^\]]+\])')
ID_RE = re.compile(r"10050\d{8,12}")


def fetch(url: str, timeout: int = 28, accept: str = "text/html,*/*;q=0.8") -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": accept,
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
            "Referer": "https://pt.aliexpress.com/",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as resp:
        return resp.read().decode("utf-8", "replace")


def fetch_bytes(url: str, timeout: int = 25) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept": "image/jpeg,image/*;q=0.8", "Referer": "https://pt.aliexpress.com/"},
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


def item_id_from_url(url: str) -> str:
    match = ITEM_RE.search(url or "")
    return match.group(1) if match else ""


def clean_img(url: str) -> str:
    url = url.split("?")[0]
    url = re.sub(r"_\d+x\d+[^./]*\.(?:jpg|jpeg|png|webp)$", ".jpg", url, flags=re.I)
    url = re.sub(r"_\.webp$", "", url, flags=re.I)
    return url


def decode_html(html: str) -> str:
    return html.replace("&quot;", '"').replace("\\/", "/")


def parse_listings(html: str) -> dict[str, list[str]]:
    text = decode_html(html)
    grouped: dict[str, list[str]] = {}
    for match in ORIG_RE.finditer(text):
        img = clean_img(match.group(1))
        window = text[max(0, match.start() - 800) : match.end() + 800]
        ids = ITEM_RE.findall(window)
        if not ids:
            continue
        grouped.setdefault(ids[0], [])
        if img not in grouped[ids[0]]:
            grouped[ids[0]].append(img)
    if not grouped:
        for item_id in unique(ITEM_RE.findall(text) + ID_RE.findall(text)):
            grouped.setdefault(item_id, [])
    return grouped


def reverse_item_ids(image_url: str) -> list[str]:
    encoded = urllib.parse.quote(image_url)
    pages = [
        "https://yandex.ru/images/search?rpt=imageview&url=" + encoded,
        "https://yandex.ru/images/search?rpt=imageview&cbir_page=sites&url=" + encoded,
        "https://yandex.com/images/search?rpt=imageview&url=" + encoded,
    ]
    found: list[str] = []
    for url in pages:
        try:
            html = fetch(url, timeout=36)
        except Exception:
            continue
        found.extend(ITEM_RE.findall(decode_html(html)))
        found.extend(ID_RE.findall(html))
        if found:
            break
    return unique(found)


def search_listings(query: str) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    urls = [
        "https://yandex.ru/images/search?text=" + urllib.parse.quote(f"{query} aliexpress"),
        "https://yandex.com/images/search?text=" + urllib.parse.quote(f"{query} aliexpress"),
    ]
    for url in urls:
        try:
            html = fetch(url, timeout=36)
        except Exception:
            continue
        found = parse_listings(html)
        for item_id, photos in found.items():
            grouped.setdefault(item_id, [])
            for photo in photos:
                if photo not in grouped[item_id]:
                    grouped[item_id].append(photo)
        if grouped:
            break
    return grouped


def search_item_ids(query: str) -> list[str]:
    return list(search_listings(query).keys())


def item_gallery(item_id: str) -> list[str]:
    html = ""
    for host in (
        "pt.aliexpress.com",
        "www.aliexpress.com",
        "aliexpress.ru",
        "www.aliexpress.ru",
    ):
        try:
            html = fetch(f"https://{host}/item/{item_id}.html", timeout=32)
        except Exception:
            continue
        if "punish" in html.lower() or "x5secdata" in html:
            continue
        if "imagePathList" in html or IMG_RE.search(html):
            break
    if not html or "punish" in html.lower() or "x5secdata" in html:
        return []
    match = PATH_RE.search(html)
    if match:
        try:
            paths = json.loads(match.group(1))
            return unique(clean_img(str(url)) for url in paths if str(url).startswith("http"))
        except json.JSONDecodeError:
            pass
    return unique(clean_img(url) for url in IMG_RE.findall(html))


def decode_photo(data: bytes) -> Image.Image | None:
    if len(data) < 2500:
        return None
    try:
        image = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:
        return None
    if min(image.size) < 80:
        return None
    return image


def pull_photo(url: str) -> Image.Image | None:
    hosts = [
        url,
        url.replace("ae-pic-a1.aliexpress-media.com", "ae01.alicdn.com"),
        url.replace("ae-pic-a1.aliexpress-media.com", "ae04.alicdn.com"),
        url.replace("ae04.alicdn.com", "ae01.alicdn.com"),
        url.replace("ae01.alicdn.com", "ae04.alicdn.com"),
    ]
    candidates: list[str] = []
    for host in unique(hosts):
        candidates.append(host)
        if not host.endswith("_640x640.jpg"):
            candidates.append(host + "_640x640.jpg")
    for candidate in candidates:
        try:
            image = decode_photo(fetch_bytes(candidate))
        except Exception:
            image = None
        if image:
            return image
    return None


def save_gallery(pid: str, urls: list[str]) -> list[str]:
    saved: list[str] = []
    hashes: set[int] = set()
    suffixes = ["", "-2", "-3"]
    for url in urls:
        if len(saved) >= 3:
            break
        image = pull_photo(url)
        if not image:
            continue
        digest = hash(image.resize((24, 24)).tobytes())
        if digest in hashes:
            continue
        dest = OUT / f"{pid}{suffixes[len(saved)]}.jpg"
        image.save(dest, "JPEG", quality=90, optimize=True)
        hashes.add(digest)
        saved.append(f"assets/img/ali/{dest.name}")
    extra = OUT / f"{pid}-4.jpg"
    if extra.exists():
        extra.unlink()
    return saved


def already_good(item: dict) -> bool:
    photos = item.get("images") or []
    if len(photos) < 2:
        return False
    return all((ROOT / src).exists() and (ROOT / src).stat().st_size > 4000 for src in photos[:2])


def fill_one(item: dict) -> tuple[str, int, str]:
    pid = item["id"]
    known = item_id_from_url(item.get("supplierUrl") or "")
    listings: dict[str, list[str]] = {}
    if known:
        listings[known] = []
    queries = []
    if item.get("search"):
        queries.append(item["search"])
    if item.get("name") and item["name"] not in queries:
        queries.append(item["name"])
    for query in queries:
        found = search_listings(query)
        for item_id, photos in found.items():
            listings.setdefault(item_id, [])
            for photo in photos:
                if photo not in listings[item_id]:
                    listings[item_id].append(photo)
        if listings:
            break
    if not listings and (OUT / f"{pid}.jpg").exists():
        for item_id in reverse_item_ids(f"https://alvaloja.store/assets/img/ali/{pid}.jpg")[:6]:
            listings.setdefault(item_id, [])

    last = "sem-anuncio"
    ranked = sorted(listings.items(), key=lambda kv: (-len(kv[1]), 0 if kv[0] == known else 1))
    for candidate, indexed in ranked[:10]:
        gallery = unique(indexed)
        if len(gallery) < 2:
            try:
                gallery = unique(gallery + item_gallery(candidate))
            except Exception as exc:
                last = f"item-erro:{exc}"
                continue
        if len(gallery) < 2:
            last = f"galeria-curta:{candidate}"
            continue
        saved = save_gallery(pid, gallery)
        if len(saved) < 2:
            last = f"download:{candidate}:{len(saved)}"
            continue
        item["supplierUrl"] = f"https://pt.aliexpress.com/item/{candidate}.html"
        item["image"] = saved[0]
        item["images"] = saved
        return pid, len(saved), candidate
    return pid, 0, last


def main() -> None:
    import sys

    limit = 0
    if len(sys.argv) > 1:
        limit = int(sys.argv[1])
    products = json.loads(SRC.read_text(encoding="utf-8"))
    todo = [item for item in products if not already_good(item)]
    if limit:
        todo = todo[:limit]
    print(f"galeria oficial: {len(todo)} produtos", flush=True)
    ok = 0
    fail = 0
    for index, item in enumerate(todo, 1):
        try:
            pid, count, item_id = fill_one(item)
        except Exception as exc:
            pid, count, item_id = item["id"], 0, str(exc)
        if count >= 2:
            ok += 1
            print(f"ok {index}/{len(todo)} {pid} +{count} {item_id}", flush=True)
        else:
            fail += 1
            print(f"fail {index}/{len(todo)} {pid} {item_id}", flush=True)
        if index % 5 == 0:
            SRC.write_text(json.dumps(products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        time.sleep(2.4)
    SRC.write_text(json.dumps(products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sizes: dict[int, int] = {}
    for item in products:
        n = len(item.get("images") or [])
        sizes[n] = sizes.get(n, 0) + 1
    print("done ok", ok, "fail", fail, "sizes", dict(sorted(sizes.items())))


if __name__ == "__main__":
    main()
