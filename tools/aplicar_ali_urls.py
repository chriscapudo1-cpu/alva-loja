"""Aplica URLs de foto reais do AliExpress já coletadas."""
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "img" / "ali"
OUT.mkdir(parents=True, exist_ok=True)
UA = "Mozilla/5.0"

# id -> (foto original AliExpress, anúncio)
MAP = {
    "tech-001": ("https://ae-pic-a1.aliexpress-media.com/kf/S1f092631b22e43949559162a94507305g.jpg", "https://pt.aliexpress.com/item/1005010391183440.html"),
    "tech-002": ("https://ae-pic-a1.aliexpress-media.com/kf/S173c05d7f54a46a38949ae5d4d1ca0f3c.jpg", "https://pt.aliexpress.com/item/1005010802856880.html"),
    "tech-003": ("https://ae-pic-a1.aliexpress-media.com/kf/S0108583e3ed24cdbb3440e7309b113596.jpg", "https://pt.aliexpress.com/item/1005009841006834.html"),
    "tech-004": ("https://ae-pic-a1.aliexpress-media.com/kf/S00c54284b6c846dd8d1f85f5b985ecf0p.jpg", "https://pt.aliexpress.com/item/1005006904617360.html"),
    "tech-005": ("https://ae-pic-a1.aliexpress-media.com/kf/Sd4e0157490864f719b4648240dff06a6u.jpg", "https://pt.aliexpress.com/item/1005008908936664.html"),
    "tech-006": ("https://ae-pic-a1.aliexpress-media.com/kf/Saed558f1704343ce8b9394dc160f3eefI.jpg", "https://pt.aliexpress.com/item/1005012242507031.html"),
    "tech-007": ("https://ae-pic-a1.aliexpress-media.com/kf/S61ea1c3b63b748719aeca26d52e0046df.jpg", "https://pt.aliexpress.com/item/1005010796075440.html"),
    "tech-008": ("https://ae-pic-a1.aliexpress-media.com/kf/Sd1c35935b88241458e583a9f38d5fc188.jpg", "https://pt.aliexpress.com/item/1005009905569823.html"),
    "tech-009": ("https://ae-pic-a1.aliexpress-media.com/kf/S8d96e399ebb24f6eab9f044dc5c89447p.jpg", "https://pt.aliexpress.com/item/1005012775965431.html"),
    "tech-010": ("https://ae-pic-a1.aliexpress-media.com/kf/S01e7ceaf0988475c87d616db29744ef9U.jpg", "https://pt.aliexpress.com/item/1005007398525395.html"),
}


def pull(url: str) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = resp.read()
        if len(data) > 4000 and data[:3] == b"\xff\xd8\xff":
            return data
    except Exception:
        pass
    alt = url.replace("ae-pic-a1.aliexpress-media.com", "ae01.alicdn.com")
    try:
        req = urllib.request.Request(alt, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = resp.read()
        if len(data) > 4000:
            return data
    except Exception:
        return None
    return None


def main() -> None:
    products = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))
    ok = 0
    for item in products:
        if item["id"] not in MAP:
            continue
        img, link = MAP[item["id"]]
        dest = OUT / f"{item['id']}.jpg"
        data = pull(img)
        if not data:
            print("fail", item["id"])
            continue
        dest.write_bytes(data)
        item["image"] = f"assets/img/ali/{item['id']}.jpg"
        item["supplierUrl"] = link
        ok += 1
        print("ok", item["id"], dest.stat().st_size)
    (ROOT / "data" / "products.json").write_text(
        json.dumps(products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("applied", ok)


if __name__ == "__main__":
    main()
