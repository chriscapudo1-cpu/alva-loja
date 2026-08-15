"""Descrições no estilo de anúncio (título + ficha + o que acompanha). Sem fornecedor."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "products.json"

PT = {
    "tws": "TWS",
    "earbuds": "fones intra-auriculares",
    "bluetooth": "Bluetooth",
    "wireless": "sem fio",
    "wired": "com fio",
    "sports": "esportivo",
    "hook": "gancho",
    "gamer": "gamer",
    "rgb": "RGB",
    "bone": "condução óssea",
    "conduction": "condução",
    "smartwatch": "relógio inteligente",
    "watch": "relógio",
    "charger": "carregador",
    "mag": "magnético",
    "magnetic": "magnético",
    "power": "energia",
    "bank": "portátil",
    "cable": "cabo",
    "usb": "USB",
    "usb-c": "USB-C",
    "type-c": "USB-C",
    "hub": "hub",
    "case": "capa",
    "silicone": "silicone",
    "iphone": "iPhone",
    "android": "Android",
    "matte": "fosca",
    "privacy": "privacidade",
    "screen": "tela",
    "protector": "protetor",
    "desktop": "mesa",
    "phone": "celular",
    "stand": "suporte",
    "adjustable": "ajustável",
    "mini": "mini",
    "portable": "portátil",
    "projector": "projetor",
    "slim": "slim",
    "keyboard": "teclado",
    "silent": "silencioso",
    "mouse": "mouse",
    "webcam": "webcam",
    "autofocus": "foco automático",
    "ring": "anel",
    "light": "luz",
    "inch": "polegadas",
    "hdmi": "HDMI",
    "adapter": "adaptador",
    "4k": "4K",
    "sofa": "sofá",
    "cover": "capa",
    "seater": "lugares",
    "stretch": "elástica",
    "jewelry": "joias",
    "organizer": "organizador",
    "box": "caixa",
    "lumbar": "lombar",
    "support": "suporte",
    "pillow": "almofada",
    "cervical": "cervical",
    "memory": "memória",
    "foam": "espuma",
    "broom": "vassoura",
    "holder": "suporte",
    "wall": "parede",
    "mount": "fixação",
    "stove": "fogão",
    "burner": "boca",
    "covers": "capas",
    "blackout": "blackout",
    "curtains": "cortina",
    "living": "sala",
    "room": "ambiente",
    "hallway": "corredor",
    "runner": "passadeira",
    "rug": "tapete",
    "desk": "mesa",
    "lamp": "luminária",
    "led": "LED",
    "dimmable": "com dimmer",
    "strip": "fita",
    "lights": "luzes",
    "humidifier": "umidificador",
    "modern": "moderno",
    "clock": "relógio",
    "over": "sobre",
    "door": "porta",
    "hook": "gancho",
    "hanger": "cabideiro",
    "foldable": "dobrável",
    "storage": "organização",
    "corner": "quina",
    "guards": "protetores",
    "baby": "bebê",
    "safety": "segurança",
    "self": "auto",
    "adhesive": "adesivo",
    "drawer": "gaveta",
    "handle": "puxador",
    "retractable": "retratil",
    "clothes": "roupa",
    "line": "varal",
    "microfiber": "microfibra",
    "cleaning": "limpeza",
    "cloths": "panos",
    "pedal": "pedal",
    "trash": "lixo",
    "can": "lixeira",
    "cat": "gato",
    "cave": "caverna",
    "bed": "cama",
    "felt": "feltro",
    "orthopedic": "ortopédica",
    "dog": "cão",
    "rechargeable": "recarregável",
    "collar": "coleira",
    "leash": "guia",
    "slow": "lento",
    "feeder": "comedouro",
    "bowl": "tigela",
    "water": "água",
    "fountain": "fonte",
    "scratching": "arranhador",
    "tower": "torre",
    "laser": "laser",
    "toy": "brinquedo",
    "automatic": "automático",
    "poop": "higiênico",
    "bag": "sacola",
    "dispenser": "dispenser",
    "winter": "inverno",
    "coat": "roupa",
    "no": "anti",
    "pull": "puxão",
    "harness": "peitoral",
    "pet": "pet",
    "hair": "pelo",
    "remover": "removedor",
    "brush": "escova",
    "washable": "lavável",
    "puppy": "filhote",
    "pad": "tapete",
    "chew": "mordedor",
    "nylon": "nylon",
    "window": "janela",
    "perch": "cama",
    "elevated": "elevado",
    "gps": "GPS",
    "tracker": "rastreador",
    "tunnel": "túnel",
    "carrier": "transporte",
    "airline": "viagem",
    "crossbody": "transversal",
    "pu": "PU",
    "leather": "couro",
    "tote": "shopper",
    "rfid": "RFID",
    "wallet": "carteira",
    "belt": "cinto",
    "men": "masculino",
    "uv400": "UV400",
    "sunglasses": "óculos de sol",
    "curved": "curva",
    "brim": "aba",
    "cap": "boné",
    "invisible": "invisível",
    "socks": "meias",
    "pairs": "pares",
    "satin": "cetim",
    "silk": "seda",
    "scarf": "lenço",
    "quartz": "quartzo",
    "strap": "pulseira",
    "stainless": "aço inox",
    "hoop": "argola",
    "earrings": "brincos",
    "thin": "fina",
    "chain": "corrente",
    "necklace": "colar",
    "bracelet": "pulseira",
    "travel": "viagem",
    "toiletry": "higiene",
    "women": "feminino",
    "dress": "vestido",
    "bucket": "bucket",
    "hat": "chapéu",
    "cotton": "algodão",
    "laptop": "notebook",
    "backpack": "mochila",
    "running": "corrida",
    "waist": "cintura",
    "touchscreen": "touchscreen",
    "gloves": "luvas",
    "knit": "tricot",
    "unisex": "unissex",
    "metal": "metal",
    "card": "cartão",
    "car": "carro",
    "suction": "ventosa",
    "air": "ar",
    "vent": "saída de ar",
    "dash": "painel",
    "cam": "câmera",
    "vacuum": "aspirador",
    "backseat": "banco traseiro",
    "rear": "ré",
    "view": "visão",
    "camera": "câmera",
    "universal": "universal",
    "floor": "assoalho",
    "mat": "tapete",
    "windshield": "para-brisa",
    "sun": "sol",
    "shade": "protetor",
    "freshener": "aromatizador",
    "clip": "clip",
    "emergency": "emergência",
    "kit": "kit",
    "headrest": "encosto",
    "tablet": "tablet",
    "steering": "volante",
    "wheel": "volante",
    "interior": "interno",
    "compressor": "compressor",
    "inverter": "inversor",
    "anti": "anti",
    "fog": "embaçante",
    "set": "conjunto",
    "electric": "elétrico",
    "neck": "pescoço",
    "massager": "massageador",
    "facial": "facial",
    "straightener": "alisadora",
    "dryer": "secador",
    "makeup": "maquiagem",
    "mirror": "espelho",
    "epilator": "depilador",
    "skincare": "skincare",
    "roller": "rolo",
    "nose": "nariz",
    "trimmer": "aparador",
    "sonic": "sônico",
    "curler": "modelador",
    "blackhead": "cravos",
    "foot": "pés",
    "file": "lixa",
    "manicure": "manicure",
    "mini": "mini",
    "headband": "faixa",
    "tweezers": "pinça",
    "nano": "nano",
    "spray": "spray",
    "scalp": "couro cabeludo",
    "beard": "barba",
    "yoga": "yoga",
    "thick": "grosso",
    "compression": "compressão",
    "jump": "pular",
    "rope": "corda",
    "resistance": "resistência",
    "bands": "elásticos",
    "foam": "espuma",
    "bottle": "garrafa",
    "gym": "academia",
    "ankle": "canela",
    "weights": "peso",
    "pilates": "pilates",
    "ball": "bola",
    "exercise": "exercício",
    "bike": "bike",
    "cooling": "ventilado",
    "speaker": "caixa de som",
    "flexible": "flexível",
    "tripod": "tripé",
    "reader": "leitor",
    "sd": "SD",
    "external": "externo",
    "ssd": "SSD",
    "flash": "pen drive",
    "lavalier": "lapela",
    "microphone": "microfone",
    "gimbal": "gimbal",
    "stabilizer": "estabilizador",
    "smartphone": "celular",
    "airpods": "AirPods",
    "lens": "lente",
    "port": "porta",
    "charging": "carregamento",
    "station": "estação",
    "lightning": "Lightning",
    "dual": "duplo",
    "wifi": "Wi-Fi",
    "switch": "switch",
    "controller": "controle",
    "game": "game",
    "vr": "VR",
    "glasses": "óculos",
    "semiconductor": "semicondutor",
    "cooler": "cooler",
    "gas": "gás",
    "spring": "mola",
    "monitor": "monitor",
    "arm": "braço",
    "mechanical": "mecânico",
    "percent": "%",
    "gaming": "gamer",
    "headset": "headset",
    "large": "grande",
    "condenser": "condensador",
    "action": "ação",
    "waterproof": "à prova d'água",
    "robot": "robô",
    "rain": "chuva",
    "drip": "pingo",
    "guard": "protetor",
    "ramp": "rampa",
    "trucker": "trucker",
    "mesh": "telinha",
    "poncho": "capa de chuva",
    "liquid": "líquida",
    "wax": "cera",
    "ionic": "iônico",
    "uv": "UV",
    "nail": "unhas",
    "suspension": "suspensão",
    "trainer": "treino",
    "straps": "fitas",
    "camping": "camping",
    "sleeping": "dormir",
    "floating": "flutuante",
    "bath": "banho",
    "thermometer": "termômetro",
    "office": "escritório",
    "chair": "cadeira",
    "paper": "papel",
    "cutter": "guilhotina",
    "rotisserie": "espeto",
    "skewer": "espeto",
}

PACK = {
    "Tech": ["1 unidade", "Cabo ou acessório de uso, quando o modelo incluir", "Manual básico"],
    "Casa": ["1 unidade", "Itens de fixação, quando o modelo incluir", "Manual básico"],
    "Pet": ["1 unidade", "Acessórios do modelo, quando inclusos", "Manual básico"],
    "Moda": ["1 unidade", "Embalagem para envio"],
    "Carro": ["1 unidade", "Itens de instalação, quando o modelo incluir", "Manual básico"],
    "Beleza": ["1 unidade", "Acessórios do modelo, quando inclusos", "Manual básico"],
    "Esporte": ["1 unidade", "Acessórios do modelo, quando inclusos"],
    "Bebê": ["1 unidade", "Acessórios do modelo, quando inclusos", "Manual básico"],
    "Escritório": ["1 unidade", "Itens de montagem, quando o modelo incluir"],
    "Cozinha": ["1 unidade", "Acessórios do modelo, quando inclusos"],
}

FEATS = [
    (("bluetooth", "tws", "wireless", "sem fio"), "Conexão sem fio, sem cabo enrolado no uso diário."),
    (("usb-c", "usb c", "type-c"), "Entrada ou recarga em USB-C."),
    (("lightning",), "Compatível com conector Lightning."),
    (("led", "rgb"), "Iluminação LED para uso à noite ou detalhe visual."),
    (("inox", "stainless", "aço"), "Acabamento em aço inox, mais fácil de limpar."),
    (("silicone", "tpu"), "Toque em silicone ou TPU, flexível no dia a dia."),
    (("impermeável", "waterproof", "ipx", "water"), "Melhor resistência à água no uso comum."),
    (("ajustável", "adjustable"), "Tamanho ou ângulo ajustável."),
    (("portátil", "portable", "mini", "viagem", "travel"), "Formato compacto para levar na bolsa."),
    (("recarregável", "rechargeable"), "Recarregável, sem ficar trocando pilha o tempo todo."),
    (("kit", "pack", "par", "set", "pairs"), "Vai em conjunto, pronto para usar."),
    (("rfid",), "Proteção RFID para cartão."),
    (("uv400", "uv"), "Proteção UV no uso ao ar livre."),
    (("ortopéd", "orthopedic", "memory foam", "cervical", "lombar", "lumbar"), "Apoio pensado para o corpo no uso prolongado."),
    (("blackout",), "Tecido que reduz a entrada de luz."),
    (("4k", "1080p", "full hd"), "Imagem em alta definição no modelo indicado."),
    (("gps",), "Localização por GPS no modelo indicado."),
    (("quiet", "silent", "silencios"), "Uso mais silencioso no dia a dia."),
    (("foldable", "dobrável", "retractable", "retrátil"), "Dobra ou recolhe para guardar."),
    (("magnetic", "ímã", "ima", "mag "), "Fixação ou encaixe magnético."),
]


def tokens(text: str) -> list[str]:
    parts = re.split(r"[\s+/_,;|]+", text.lower())
    out = []
    for part in parts:
        part = part.strip(".-")
        if part:
            out.append(part)
    return out


def title_line(item: dict) -> str:
    search = item.get("search") or ""
    bits = []
    for tok in tokens(search):
        bits.append(PT.get(tok, tok))
    extra = " ".join(bits).strip()
    name = item["name"]
    if extra and extra.lower() not in name.lower():
        return f"{name} {extra}"
    return name


def has_word(hay: str, *words: str) -> bool:
    return any(re.search(rf"(?<![a-z0-9]){re.escape(word)}(?![a-z0-9])", hay) for word in words)


def specs(item: dict) -> list[str]:
    hay = f"{item['name']} {item.get('search') or ''}".lower()
    rows = [f"Tipo: {item['name']}", f"Categoria: {item['tag']}"]
    if has_word(hay, "bluetooth", "tws", "wireless"):
        ver = "5.3" if "5.3" in hay else "sem fio"
        rows.append(f"Conexão: Bluetooth {ver}".replace("Bluetooth sem fio", "Bluetooth"))
    if has_word(hay, "usb-c", "type-c") or "usb c" in hay:
        rows.append("Conector: USB-C")
    if has_word(hay, "lightning"):
        rows.append("Conector: Lightning")
    if has_word(hay, "silicone", "tpu"):
        rows.append("Material: silicone / TPU")
    elif has_word(hay, "inox", "stainless", "aço"):
        rows.append("Material: aço inox")
    elif has_word(hay, "nylon"):
        rows.append("Material: nylon")
    elif has_word(hay, "cotton", "algodão"):
        rows.append("Material: algodão")
    elif has_word(hay, "leather", "couro") or has_word(hay, "pu"):
        rows.append("Material: couro PU")
    elif has_word(hay, "abs", "plastic", "plástico"):
        rows.append("Material: plástico de uso diário")
    if any(k in hay for k in ("ipx", "waterproof", "impermeável")):
        rows.append("Resistência: melhor vedação contra respingos")
    if re.search(r"\b(\d+)\s*w\b", hay):
        rows.append(f"Potência: {re.search(r'(\d+)\s*w', hay).group(1)} W")
    if re.search(r"\b(\d+)\s*mah\b", hay):
        rows.append(f"Bateria: {re.search(r'(\d+)\s*mah', hay).group(1)} mAh")
    if re.search(r"\b(\d+)\s*ml\b", hay):
        rows.append(f"Capacidade: {re.search(r'(\d+)\s*ml', hay).group(1)} ml")
    if re.search(r"\b(\d+)\s*m\b", hay):
        rows.append(f"Comprimento: {re.search(r'(\d+)\s*m', hay).group(1)} m")
    if re.search(r"\b(\d+)\s*gb\b", hay):
        rows.append(f"Capacidade: {re.search(r'(\d+)\s*gb', hay).group(1)} GB")
    if any(k in hay for k in ("rechargeable", "recarregável")):
        rows.append("Alimentação: recarregável")
    rows.append("Uso: residencial / dia a dia")
    # unique preserve order
    seen: set[str] = set()
    out = []
    for row in rows:
        if row not in seen:
            seen.add(row)
            out.append(row)
    return out


def features(item: dict) -> list[str]:
    hay = f"{item['name']} {item.get('search') or ''}".lower()
    found = []
    for keys, line in FEATS:
        if any(k in hay for k in keys):
            found.append(line)
        if len(found) == 4:
            break
    if not found:
        found.append("Peça escolhida para uso direto, sem instalação complicada.")
        found.append("Acabamento de uso diário, fácil de guardar.")
    return found


def describe(item: dict) -> str:
    title = title_line(item)
    feat = "\n".join(f"- {line}" for line in features(item))
    spec = "\n".join(f"- {line}" for line in specs(item))
    pack = "\n".join(f"- {line}" for line in PACK.get(item["tag"], PACK["Tech"]))
    return (
        f"{title}\n\n"
        f"Características\n{feat}\n\n"
        f"Especificações\n{spec}\n\n"
        f"O que acompanha\n{pack}\n\n"
        "A cor e o acabamento podem variar levemente conforme o lote. "
        "Envio após a confirmação do pagamento."
    )


def main() -> None:
    products = json.loads(SRC.read_text(encoding="utf-8"))
    for item in products:
        cover = item.get("image") or f"assets/img/ali/{item['id']}.jpg"
        item["image"] = cover
        item["images"] = [cover]
        item["description"] = describe(item)
    SRC.write_text(json.dumps(products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(products)} descrições no estilo de anúncio")


if __name__ == "__main__":
    main()
