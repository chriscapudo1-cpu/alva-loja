# Variedades só nos produtos que pedem (cor/tamanho/modelo), com a cor da foto.
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = ROOT / "data" / "products.json"

SWATCHES = {
    "Preto": (28, 28, 28),
    "Grafite": (58, 58, 58),
    "Cinza": (138, 138, 138),
    "Prata": (180, 180, 185),
    "Inox": (168, 174, 180),
    "Branco": (244, 241, 234),
    "Off-white": (238, 232, 220),
    "Bege": (215, 196, 163),
    "Nude": (224, 200, 176),
    "Camel": (196, 154, 108),
    "Marrom": (107, 68, 35),
    "Azul": (42, 82, 150),
    "Verde": (56, 118, 78),
    "Militar": (77, 92, 58),
    "Vermelho": (178, 38, 40),
    "Vinho": (110, 36, 48),
    "Rosa": (212, 138, 155),
    "Lilás": (155, 122, 179),
    "Roxo": (107, 74, 140),
    "Amarelo": (212, 180, 74),
    "Laranja": (212, 120, 58),
    "Dourado": (196, 163, 106),
    "Transparente": (186, 192, 198),
}

HEX = {name: f"#{r:02x}{g:02x}{b:02x}" for name, (r, g, b) in SWATCHES.items()}

SIZE = re.compile(
    r"(meia |meias |luva |luvas |cinto |bone |chapeu |cachecol|"
    r"lenco seda|lenco pescoco|lenco bolso|pijama|body manga|"
    r"chinelo|joelheira|segunda pele|peitoral|coleira|focinheira|"
    r"guia retratil|guia maos|roupa cao|roupa gato|legging|moletom|"
    r"jaqueta|bermuda|short |blusa |camisa |vestido |calca |"
    r"headband|caneleira 2kg)"
)
COLOR_KIND = re.compile(
    r"(capa de sofa|capa sofa|cortina|edredom|jogo de cama|capa colchao|"
    r"tapete sala|tapete passadeira|tapete banheiro|almofada|lencol|"
    r"bolsa|mochila|carteira|cinto |bone |chapeu |cachecol|lenco seda|"
    r"oculos|meia |luva |pijama|chinelo|necessaire|pochete|"
    r"coleira|peitoral|cama caverna|cama ortopedica|cama janela|cama donut|"
    r"roupa cao|roupa gato|guia retratil|"
    r"capa iphone|capa android|capa airpods|capa volante|"
    r"cabo usb|cabo lightning|cabo displayport|"
    r"tapete yoga)"
)


def fold(value: str) -> str:
    text = unicodedata.normalize("NFD", str(value or "").lower())
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


def extra_option(name: str) -> dict | None:
    if "capa iphone" in name or "pelicula privacidade" in name or "pelicula camera iphone" in name:
        return {"name": "Modelo", "values": ["iPhone 13", "iPhone 14", "iPhone 15", "iPhone 16"]}
    if "capa android" in name:
        return {"name": "Modelo", "values": ["Universal", "Samsung", "Xiaomi", "Motorola"]}
    if "capa airpods" in name:
        return {"name": "Modelo", "values": ["AirPods 1/2", "AirPods 3", "AirPods Pro"]}
    if "capa macbook" in name:
        return {"name": "Tamanho", "values": ['13"', '14"', '16"']}
    if "cabo ethernet" in name:
        return {"name": "Comprimento", "values": ["2 m", "5 m", "10 m"]}
    if re.search(r"cabo usb|cabo lightning|cabo displayport", name):
        return {"name": "Comprimento", "values": ["0,5 m", "1 m", "2 m"]}
    if "capa de sofa" in name or "capa sofa" in name:
        return {"name": "Tamanho", "values": ["2 lugares", "3 lugares", "4 lugares"]}
    if re.search(r"edredom|jogo de cama|capa colchao", name):
        return {"name": "Tamanho", "values": ["Solteiro", "Casal", "Queen", "King"]}
    if re.search(r"cortina blackout|cortina voil|cortina box", name):
        return {"name": "Medida", "values": ["2,00×1,80 m", "2,80×2,30 m", "3,00×2,50 m"]}
    if re.search(r"tapete sala|tapete passadeira|tapete banheiro", name):
        return {"name": "Medida", "values": ["40×60 cm", "60×90 cm", "80×150 cm"]}
    if "tapete yoga" in name:
        return {"name": "Espessura", "values": ["6 mm", "8 mm", "10 mm"]}
    if re.search(
        r"cama caverna|cama ortopedica|cama janela|cama donut|tenda cama|cama aquecida",
        name,
    ):
        return {"name": "Tamanho", "values": ["P", "M", "G"]}
    if "luvas boxe" in name:
        return {"name": "Tamanho", "values": ["10 oz", "12 oz", "14 oz"]}
    if "capa volante" in name:
        return {"name": "Tamanho", "values": ["37–38 cm", "38–39 cm", "39–40 cm"]}
    if SIZE.search(name):
        return {"name": "Tamanho", "values": ["P", "M", "G", "GG"]}
    return None


def needs_color(name: str) -> bool:
    if "pelicula" in name and "capa" not in name:
        return False
    return bool(COLOR_KIND.search(name))


def extras_for(name: str) -> list[str]:
    if re.search(r"capa iphone|capa android|capa airpods", name):
        return ["Preto", "Transparente", "Branco"]
    if "cabo" in name:
        return ["Preto", "Branco"]
    if re.search(r"capa de sofa|cortina|edredom|jogo de cama|tapete", name):
        return ["Cinza", "Bege", "Preto", "Azul"]
    if re.search(r"coleira|peitoral|cama |roupa cao|roupa gato", name):
        return ["Cinza", "Bege", "Preto"]
    if re.search(r"bolsa|carteira|cinto|bone|chapeu|lenco|cachecol", name):
        return ["Preto", "Bege", "Marrom", "Branco"]
    return ["Preto", "Cinza", "Bege"]


def is_skin(r: int, g: int, b: int) -> bool:
    return r > 80 and g > 40 and b > 20 and r > g > b - 10 and (r - g) > 12 and r - b > 15


def is_sky(r: int, g: int, b: int) -> bool:
    return b > 140 and b > r + 12 and b >= g - 5


def sample_rgb(path: Path) -> tuple[int, int, int] | None:
    if not path.exists():
        return None
    try:
        im = Image.open(path).convert("RGB")
    except OSError:
        return None
    im.thumbnail((160, 160))
    w, h = im.size
    counts: dict[tuple[int, int, int], int] = {}
    for y in range(int(h * 0.20), int(h * 0.82) or h):
        for x in range(int(w * 0.18), int(w * 0.82) or w):
            r, g, b = im.getpixel((x, y))
            mx, mn = max(r, g, b), min(r, g, b)
            if r > 232 and g > 228 and b > 220:
                continue
            if mx > 208 and (mx - mn) < 20:
                continue
            if is_skin(r, g, b) or is_sky(r, g, b):
                continue
            key = (r // 10 * 10, g // 10 * 10, b // 10 * 10)
            counts[key] = counts.get(key, 0) + 1
    if not counts:
        return None
    ranked = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    for rgb, _count in ranked:
        r, g, b = rgb
        if max(r, g, b) < 40 and min(r, g, b) < 18:
            continue
        return rgb
    return ranked[0][0]


def nearest_name(rgb: tuple[int, int, int], name: str) -> str:
    r, g, b = rgb
    sat = max(r, g, b) - min(r, g, b)
    if "capa iphone" in name or "capa android" in name or "capa airpods" in name:
        if sat < 55:
            return "Transparente"
    if r > 110 and r > g * 1.7 and r > b * 1.7:
        return "Vermelho" if r > 130 else "Vinho"
    if sat < 18 and max(r, g, b) < 55:
        return "Preto"
    if sat < 18 and max(r, g, b) > 200:
        return "Branco"
    if sat < 22 and 70 <= max(r, g, b) <= 175:
        return "Cinza"
    best = "Cinza"
    best_d = 10**9
    for label, (R, G, B) in SWATCHES.items():
        dist = (r - R) ** 2 * 0.30 + (g - G) ** 2 * 0.59 + (b - B) ** 2 * 0.11
        if sat > 45 and label in {"Branco", "Off-white", "Transparente"}:
            dist *= 1.8
        if dist < best_d:
            best_d = dist
            best = label
    return best


def to_hex(rgb: tuple[int, int, int], name: str) -> str:
    sr, sg, sb = SWATCHES.get(name, rgb)
    r = int(rgb[0] * 0.55 + sr * 0.45)
    g = int(rgb[1] * 0.55 + sg * 0.45)
    b = int(rgb[2] * 0.55 + sb * 0.45)
    return f"#{r:02x}{g:02x}{b:02x}"


def color_group(item: dict, name: str) -> dict:
    rgb = sample_rgb(ROOT / (item.get("image") or ""))
    detected = nearest_name(rgb, name) if rgb else "Preto"
    if "cabo" in name and detected in {"Off-white", "Branco", "Azul", "Lilás", "Transparente"}:
        detected = "Preto"
        rgb = SWATCHES["Preto"]
    values = [detected]
    for extra in extras_for(name):
        if extra not in values:
            values.append(extra)
        if len(values) >= 4:
            break
    group: dict = {"name": "Cor", "values": values}
    if rgb:
        group["hex"] = {detected: to_hex(rgb, detected)}
    return group


def options_for(item: dict) -> list[dict]:
    name = fold(item.get("name") or "")
    groups: list[dict] = []
    if needs_color(name):
        groups.append(color_group(item, name))
    extra = extra_option(name)
    if extra:
        groups.append(extra)
    return groups


def main() -> None:
    products = json.loads(PRODUCTS.read_text(encoding="utf-8"))
    with_opts = 0
    with_color = 0
    samples = []
    for item in products:
        opts = options_for(item)
        if opts:
            item["options"] = opts
            with_opts += 1
            if opts[0].get("name") == "Cor":
                with_color += 1
                if len(samples) < 12:
                    samples.append(f"{item['id']} {item['name']}: {opts[0]['values'][0]} {opts[0].get('hex', {})}")
        else:
            item["options"] = []
    PRODUCTS.write_text(
        json.dumps(products, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{with_opts} produtos com variedade · {with_color} com cor · {len(products) - with_opts} sem")
    for line in samples:
        print(" ", line)


if __name__ == "__main__":
    main()
