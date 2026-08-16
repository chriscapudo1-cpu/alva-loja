"""Separa só montagem oficial da mesma peça (faixa clara entre duas cenas)."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "products.json"
OUT = ROOT / "assets" / "img" / "ali"


def col_stats(pix, x: int, h: int) -> tuple[float, float]:
    vals = [pix[x, y] for y in range(0, h, max(1, h // 90))]
    mean = sum(vals) / len(vals)
    var = sum((v - mean) ** 2 for v in vals) / len(vals)
    return mean, var


def row_stats(pix, y: int, w: int) -> tuple[float, float]:
    vals = [pix[x, y] for x in range(0, w, max(1, w // 90))]
    mean = sum(vals) / len(vals)
    var = sum((v - mean) ** 2 for v in vals) / len(vals)
    return mean, var


def find_seams(image: Image.Image) -> list[tuple[str, int]]:
    gray = image.convert("L")
    pix = gray.load()
    w, h = gray.size
    seams: list[tuple[str, int]] = []
    # vertical seam
    for x in range(int(w * 0.28), int(w * 0.72)):
        mean, var = col_stats(pix, x, h)
        if mean < 225 or var > 90:
            continue
        left_m, left_v = col_stats(pix, max(0, x - 18), h)
        right_m, right_v = col_stats(pix, min(w - 1, x + 18), h)
        if left_v > 400 and right_v > 400 and left_m < 200 and right_m < 200:
            seams.append(("v", x))
            break
    # horizontal seam
    for y in range(int(h * 0.28), int(h * 0.72)):
        mean, var = row_stats(pix, y, w)
        if mean < 225 or var > 90:
            continue
        up_m, up_v = row_stats(pix, max(0, y - 18), w)
        dn_m, dn_v = row_stats(pix, min(h - 1, y + 18), w)
        if up_v > 400 and dn_v > 400 and up_m < 200 and dn_m < 200:
            seams.append(("h", y))
            break
    return seams


def split_image(path: Path) -> list[Image.Image]:
    image = Image.open(path).convert("RGB")
    w, h = image.size
    seams = find_seams(image)
    parts: list[Image.Image] = []
    for kind, pos in seams:
        if kind == "v" and pos >= 180 and w - pos >= 180:
            parts = [image.crop((0, 0, pos - 3, h)), image.crop((pos + 3, 0, w, h))]
        elif kind == "h" and pos >= 180 and h - pos >= 180:
            parts = [image.crop((0, 0, w, pos - 3)), image.crop((0, pos + 3, w, h))]
        if parts:
            break
    keep = []
    hashes = set()
    for part in parts:
        if min(part.size) < 160:
            continue
        digest = hash(part.resize((24, 24)).tobytes())
        if digest in hashes:
            continue
        hashes.add(digest)
        keep.append(part)
    return keep


def already_multi(item: dict) -> bool:
    photos = item.get("images") or []
    if len(photos) < 2:
        return False
    return all((ROOT / src).exists() and (ROOT / src).stat().st_size > 4000 for src in photos[:2])


def main() -> None:
    products = json.loads(SRC.read_text(encoding="utf-8"))
    ok = 0
    for item in products:
        if already_multi(item):
            continue
        src = ROOT / (item.get("image") or "")
        if not src.exists():
            continue
        try:
            parts = split_image(src)
        except Exception:
            continue
        if len(parts) < 2:
            continue
        saved = [item["image"]]
        for index, part in enumerate(parts[:2], 2):
            dest = OUT / f"{item['id']}-{index}.jpg"
            part.save(dest, "JPEG", quality=90, optimize=True)
            saved.append(f"assets/img/ali/{dest.name}")
        item["images"] = saved
        ok += 1
        print("ok", item["id"], "+", len(saved), flush=True)
    SRC.write_text(json.dumps(products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("montagens", ok, flush=True)


if __name__ == "__main__":
    main()
