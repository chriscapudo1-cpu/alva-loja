"""Mantém extras só se forem outra foto do mesmo produto.

Remove recorte/duplicata da principal e foto de outro modelo.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ALI = ROOT / "assets" / "img" / "ali"
SRC = ROOT / "data" / "products.json"


def ahash(path: Path, size: int = 12) -> int:
    image = Image.open(path).convert("L").resize((size, size), Image.Resampling.BILINEAR)
    pixels = list(image.getdata())
    avg = sum(pixels) / len(pixels)
    bits = 0
    for index, value in enumerate(pixels):
        if value >= avg:
            bits |= 1 << index
    return bits


def hamming(left: int, right: int) -> int:
    return (left ^ right).bit_count()


def mean_color(path: Path) -> tuple[float, float, float]:
    image = Image.open(path).convert("RGB").resize((24, 24), Image.Resampling.BILINEAR)
    pixels = list(image.getdata())
    fg = [pixel for pixel in pixels if sum(pixel) < 700] or pixels
    return tuple(sum(pixel[i] for pixel in fg) / len(fg) for i in range(3))


def color_dist(left: tuple[float, float, float], right: tuple[float, float, float]) -> float:
    return sum((left[i] - right[i]) ** 2 for i in range(3)) ** 0.5


def keep_extra(main: Path, extra: Path) -> bool:
    if not extra.exists() or extra.stat().st_size < 4000:
        return False
    try:
        distance = hamming(ahash(main), ahash(extra))
        shade = color_dist(mean_color(main), mean_color(extra))
    except Exception:
        return False
    if distance <= 8:
        return False
    if shade > 68:
        return False
    return True


def main() -> None:
    products = json.loads(SRC.read_text(encoding="utf-8"))
    kept = 0
    dropped = 0
    for item in products:
        pid = item["id"]
        main = ALI / f"{pid}.jpg"
        gallery = [f"assets/img/ali/{pid}.jpg"] if main.exists() else []
        for suffix in ("-2", "-3", "-4"):
            extra = ALI / f"{pid}{suffix}.jpg"
            if main.exists() and keep_extra(main, extra):
                gallery.append(f"assets/img/ali/{pid}{suffix}.jpg")
                kept += 1
            elif extra.exists():
                extra.unlink()
                dropped += 1
        item["image"] = gallery[0] if gallery else item.get("image") or ""
        item["images"] = gallery
    SRC.write_text(json.dumps(products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts: dict[int, int] = {}
    for item in products:
        counts[len(item.get("images") or [])] = counts.get(len(item.get("images") or []), 0) + 1
    print("kept extras", kept)
    print("dropped extras", dropped)
    print("gallery sizes", dict(sorted(counts.items())))


if __name__ == "__main__":
    main()
