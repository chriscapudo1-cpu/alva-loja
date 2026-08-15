import re
import ssl
import urllib.parse
import urllib.request
from pathlib import Path

ctx = ssl.create_default_context()
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8",
}


def fetch(url: str, timeout: int = 14) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.status, resp.read()
    except Exception as exc:
        return 0, str(exc).encode()


urls = [
    "https://pt.aliexpress.com/item/1005010391183440.html",
    "https://www.aliexpress.com/item/1005010391183440.html",
    "https://www.aliexpress.us/item/1005010391183440.html",
    "https://m.aliexpress.com/item/1005010391183440.html",
    "https://r.jina.ai/http://www.aliexpress.com/item/1005010391183440.html",
    "https://api.allorigins.win/raw?url="
    + urllib.parse.quote("https://www.aliexpress.com/item/1005010391183440.html"),
    "https://corsproxy.io/?"
    + urllib.parse.quote("https://www.aliexpress.com/item/1005010391183440.html"),
    "https://images.search.yahoo.com/search/images?p="
    + urllib.parse.quote("iphone silicone case aliexpress"),
    "https://yandex.com/images/search?text="
    + urllib.parse.quote("iphone silicone case aliexpress"),
]

out = Path("tools/_probe")
out.mkdir(exist_ok=True)

for i, url in enumerate(urls):
    code, body = fetch(url)
    text = body.decode("utf-8", "replace")
    imgs = re.findall(
        r"https?://[^\"'\s]*?(?:alicdn|aliexpress-media)\.com[^\"'\s]+",
        text,
    )
    kf = re.findall(r"kf/[A-Za-z0-9]+\.(?:jpg|png|webp)", text)
    punish = "punish" in text.lower() or "x5secdata" in text
    print(
        f"[{i}] {code} len={len(body)} imgs={len(imgs)} kf={len(kf)} punish={punish} {url[:80]}"
    )
    if imgs:
        print("   ", imgs[0][:140])
    if kf:
        print("    kf", kf[:3])
    (out / f"src{i}.txt").write_text(text[:40000], encoding="utf-8")
