"""Casa cada produto extra com a foto original mais parecida da mesma categoria."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "products.json"

ORIGINAL = {
    "Tech": range(1, 21),
    "Casa": range(21, 41),
    "Pet": range(41, 61),
    "Moda": range(61, 81),
    "Carro": range(81, 101),
    "Beleza": range(101, 121),
    "Esporte": range(121, 141),
    "Bebê": range(141, 161),
    "Escritório": range(161, 181),
    "Cozinha": range(181, 201),
}

STOP = {
    "de", "da", "do", "das", "dos", "para", "com", "sem", "em", "no", "na",
    "kit", "un", "par", "pcs", "pç", "mini", "usb", "led", "rgb", "the",
    "and", "for", "with", "set", "pack",
}

SYN = {
    "fone": {"fone", "earbud", "earbuds", "headphone", "headset", "tws"},
    "relogio": {"relogio", "watch", "smartwatch"},
    "carregador": {"carregador", "charger", "powerbank", "power"},
    "cabo": {"cabo", "cable"},
    "capa": {"capa", "case", "cover"},
    "teclado": {"teclado", "keyboard"},
    "mouse": {"mouse"},
    "webcam": {"webcam", "camera"},
    "hub": {"hub"},
    "suporte": {"suporte", "stand", "holder", "mount"},
    "projetor": {"projetor", "projector"},
    "notebook": {"notebook", "laptop"},
    "ssd": {"ssd", "hd", "disco"},
    "microfone": {"microfone", "microphone", "mic"},
    "coleira": {"coleira", "collar"},
    "guia": {"guia", "leash"},
    "peitoral": {"peitoral", "harness"},
    "cama": {"cama", "bed", "donut"},
    "comedouro": {"comedouro", "feeder", "bowl"},
    "bebedouro": {"bebedouro", "fonte", "fountain", "water"},
    "arranhador": {"arranhador", "scratch", "scratcher", "torre"},
    "brinquedo": {"brinquedo", "toy", "laser", "mordedor", "chew"},
    "bolsa": {"bolsa", "bag", "mochila", "backpack", "tote", "clutch"},
    "carteira": {"carteira", "wallet"},
    "cinto": {"cinto", "belt"},
    "oculos": {"oculos", "sunglasses", "glasses"},
    "bone": {"bone", "cap", "chapeu", "hat", "bucket"},
    "meia": {"meia", "socks"},
    "lenco": {"lenco", "cachecol", "scarf"},
    "brinco": {"brinco", "earring", "earrings"},
    "colar": {"colar", "necklace", "choker"},
    "pulseira": {"pulseira", "bracelet"},
    "camera": {"camera", "dash", "dvr", "re"},
    "aspirador": {"aspirador", "vacuum"},
    "tapete": {"tapete", "mat", "rug"},
    "luz": {"luz", "light", "led", "lampada", "luminaria"},
    "volante": {"volante", "steering"},
    "escova": {"escova", "brush"},
    "secador": {"secador", "dryer"},
    "espelho": {"espelho", "mirror"},
    "massageador": {"massageador", "massager"},
    "depilador": {"depilador", "epilator"},
    "yoga": {"yoga", "pilates"},
    "corda": {"corda", "rope", "jump"},
    "garrafa": {"garrafa", "bottle", "squeeze"},
    "luvas": {"luvas", "luva", "gloves"},
    "bike": {"bike", "bicicleta", "ciclismo"},
    "mamadeira": {"mamadeira", "bottle", "warmer"},
    "babador": {"babador", "bib"},
    "carrinho": {"carrinho", "stroller"},
    "chupeta": {"chupeta", "pacifier"},
    "fralda": {"fralda", "diaper"},
    "organizador": {"organizador", "organizadora", "organizer"},
    "luminaria": {"luminaria", "lamp", "desk"},
    "processador": {"processador", "chopper"},
    "balanca": {"balanca", "scale"},
    "airfryer": {"airfryer", "air", "fryer", "forma"},
    "panela": {"panela", "pot", "cooker"},
    "faca": {"faca", "knife", "facas"},
    "pote": {"pote", "container", "jar"},
}


def fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower()


def tokens(text: str) -> set[str]:
    words = set(re.findall(r"[a-z0-9]{3,}", fold(text)))
    words -= STOP
    extra: set[str] = set()
    for group in SYN.values():
        if words & group:
            extra |= group
    return words | extra


def num_of(pid: str) -> int | None:
    try:
        return int(str(pid).split("-")[-1])
    except ValueError:
        return None


def is_original(item: dict) -> bool:
    n = num_of(item.get("id") or "")
    return n is not None and n in ORIGINAL.get(item.get("tag") or "", ())


def score(a: set[str], b: set[str]) -> int:
    return len(a & b)


def main() -> None:
    products = json.loads(SRC.read_text(encoding="utf-8"))
    restored = 0
    for item in products:
        own = ROOT / "assets" / "img" / "ali" / f"{item['id']}.jpg"
        if own.exists() and own.stat().st_size > 4000:
            item["image"] = f"assets/img/ali/{item['id']}.jpg"
            restored += 1

    bases: dict[str, list[dict]] = {}
    for item in products:
        if is_original(item):
            item["_tok"] = tokens(f"{item['name']} {item.get('search') or ''}")
            bases.setdefault(item["tag"], []).append(item)

    changed = 0
    for item in products:
        own = ROOT / "assets" / "img" / "ali" / f"{item['id']}.jpg"
        if own.exists() and own.stat().st_size > 4000:
            continue
        pool = bases.get(item["tag"]) or []
        if not pool:
            continue
        want = tokens(f"{item['name']} {item.get('search') or ''}")
        best = max(pool, key=lambda src: score(want, src["_tok"]))
        pts = score(want, best["_tok"])
        pick = best if pts else pool[0]
        if item.get("image") != pick["image"]:
            item["image"] = pick["image"]
            changed += 1

    for item in products:
        item.pop("_tok", None)
    SRC.write_text(json.dumps(products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"originais restaurados: {restored}")
    print(f"extras casados: {changed}")


if __name__ == "__main__":
    main()
