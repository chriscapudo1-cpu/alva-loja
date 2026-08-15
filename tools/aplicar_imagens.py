# Liga cada produto à foto certa pelo nome.
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = "assets/img/cat"
DROP = "assets/img/drop"

# Mais específico primeiro — cobre os 200 originais e os 800 extras
RULES = [
    (("airfryer", "air fryer"), f"{CAT}/chopper.jpg"),
    (("ssd", "nvme", "pen drive", "hd case", "dock nvme"), f"{CAT}/powerbank.jpg"),
    (("caixa de som", "speaker"), f"{CAT}/earbuds.jpg"),
    (("microfone", "gimbal", "estabilizador"), f"{CAT}/webcam.jpg"),
    (("teclado", "mouse gamer", "mouse pad", "headset 7.1"), f"{CAT}/keyboard.jpg"),
    (("roteador", "repetidor", "antena wi-fi", "wifi", "ethernet"), f"{CAT}/powerbank.jpg"),
    (("projetor", "webcam 4k", "webcam"), f"{CAT}/webcam.jpg"),
    (("smartwatch", "relógio digital", "relogio digital", "relógio feminino", "relogio feminino", "relógio esportivo", "gps portátil", "gps pet"), f"{CAT}/smartwatch.jpg"),
    (("power bank", "carregador", "dock carregador", "fonte 650"), f"{CAT}/powerbank.jpg"),
    (("capa airpods", "capa iphone", "capa android", "capa macbook", "película", "pelicula"), f"{CAT}/phone-case.jpg"),
    (("fone", "earbud", "headphone", "headset call", "amp fone"), f"{CAT}/earbuds.jpg"),
    (("suporte notebook", "base notebook", "suporte monitor", "braço monitor", "laptop"), f"{CAT}/laptop-stand.jpg"),
    (("suporte celular", "suporte mesa", "tripé celular", "tripe celular", "bastão selfie", "suporte tablet"), f"{CAT}/car-holder.jpg"),
    (("capa de sofá", "capa de sofa", "edredom", "jogo de cama", "cortina", "persiana", "blackout"), f"{CAT}/sofa.jpg"),
    (("umidificador", "desumidificador", "purificador ar", "difusor aroma"), f"{CAT}/humidifier.jpg"),
    (("fita led", "luminária", "luminaria", "abajur", "lâmpada", "lampada", "anel led", "luz noturna"), f"{CAT}/led.jpg"),
    (("aspirador", "robô", "robo", "rodo mágico", "balde esfregão"), f"{CAT}/vacuum.jpg"),
    (("travesseiro", "almofada lombar", "edredom", "ninho", "saco dormir"), f"{DROP}/lombar.jpg"),
    (("coleira", "guia", "peitoral", "focinheira", "cinto segurança carro pet"), f"{CAT}/collar.jpg"),
    (("cama caverna", "cama janela", "arranhador", "árvore gato", "arvore gato", "túnel", "tunel", "tenda cama"), f"{CAT}/cat-bed.jpg"),
    (("cama ortopédica", "cama ortopedica", "cama donut", "cama aquecida", "casinha"), f"{CAT}/dog-bed.jpg"),
    (("comedouro", "bebedouro", "fonte água", "fonte agua", "fonte 2l"), f"{CAT}/feeder.jpg"),
    (("bolsa transporte", "mochila cápsula", "mochila capsula", "carrinho passeio pet", "bolsa maternidade", "mochila"), f"{CAT}/backpack.jpg"),
    (("bolsa", "clutch", "tote", "pochete", "necessaire", "nécessaire", "shoulder"), f"{CAT}/bag.jpg"),
    (("carteira", "porta-cartão", "porta-cartao", "porta-passaporte", "cinto", "money clip"), f"{CAT}/wallet.jpg"),
    (("óculos", "oculos", "boné", "bone", "chapéu", "chapeu", "boina", "viseira"), f"{CAT}/sunglasses.jpg"),
    (("brinco", "colar", "pulseira", "anel", "tornozeleira", "joia", "broche"), f"{CAT}/jewelry.jpg"),
    (("meia", "luva", "cachecol", "lenço", "lenco", "gorro", "scrunchie"), f"{DROP}/meias.jpg"),
    (("dash", "câmera veicular", "camera veicular", "câmera dvr", "camera dvr", "câmera de ré", "camera de re", "câmera 360", "sensor estacionamento"), f"{CAT}/dashcam.jpg"),
    (("suporte magnético", "suporte grade", "carregador indução carro", "suporte celular painel"), f"{CAT}/car-holder.jpg"),
    (("aspirador", "compressor", "macaco", "chave impacto"), f"{CAT}/vacuum.jpg"),
    (("capa banco", "capa volante", "tapete borracha", "tapete porta-malas"), f"{CAT}/yoga.jpg"),
    (("massageador de pescoço", "massageador pescoco", "massageador couro"), f"{CAT}/neck.jpg"),
    (("espelho", "massageador facial", "máscara led", "mascara led", "removedor cravos"), f"{CAT}/mirror.jpg"),
    (("escova", "secador", "chapinha", "prancha", "babyliss", "modelador", "kit barba", "depilador", "aparador", "lixa", "manicure", "unha"), f"{DROP}/escova.jpg"),
    (("tapete yoga", "pilates", "kettlebell", "anilha", "halteres", "barra", "elástico", "elastico", "corda", "ab roller", "yoga"), f"{CAT}/yoga.jpg"),
    (("bike", "ciclismo", "selim", "pedal", "capacete bike", "farol bike"), f"{CAT}/car-holder.jpg"),
    (("garrafa", "squeeze", "coqueteleira", "cantil", "hidratação", "hidratacao"), f"{CAT}/bag.jpg"),
    (("mamadeira", "aquecedor de mamadeira", "esterilizador", "bico mamadeira"), f"{CAT}/bottle-warmer.jpg"),
    (("amamentação", "amamentacao", "almofada amamentação", "bomba tira-leite", "conchas"), f"{CAT}/nursing.jpg"),
    (("babador", "mordedor", "chocalho", "chupeta", "fralda", "body", "cueiro"), f"{CAT}/nursing.jpg"),
    (("monitor bebê", "monitor bebe", "baby monitor"), f"{CAT}/webcam.jpg"),
    (("carrinho", "mosquiteiro", "organizador carrinho"), f"{CAT}/bag.jpg"),
    (("teclado", "grampeador", "etiquetadora", "calculadora", "caneta", "caderno"), f"{CAT}/keyboard.jpg"),
    (("suporte fone", "hub mesa", "hub usb"), f"{CAT}/laptop-stand.jpg"),
    (("processador", "airfryer", "panela", "cafeteira", "chaleira", "torradeira", "grill", "mixer", "liquidificador", "waffle", "moedor café"), f"{CAT}/chopper.jpg"),
    (("balança", "balanca", "termômetro", "termometro"), f"{CAT}/scale.jpg"),
    (("pote", "hermético", "hermetico", "organizador geladeira", "organizador temperos"), f"{CAT}/jewelry.jpg"),
]


FALLBACK = {
    "Tech": f"{CAT}/earbuds.jpg",
    "Casa": f"{CAT}/sofa.jpg",
    "Pet": f"{CAT}/cat-bed.jpg",
    "Moda": f"{CAT}/bag.jpg",
    "Carro": f"{CAT}/car-holder.jpg",
    "Beleza": f"{CAT}/mirror.jpg",
    "Esporte": f"{CAT}/yoga.jpg",
    "Bebê": f"{CAT}/nursing.jpg",
    "Escritório": f"{CAT}/laptop-stand.jpg",
    "Cozinha": f"{CAT}/chopper.jpg",
}


def pick(name: str, tag: str = "") -> str:
    n = name.lower()
    for keys, path in RULES:
        if any(k in n for k in keys):
            return path
    return FALLBACK.get(tag, f"{CAT}/earbuds.jpg")


def main() -> None:
    path = ROOT / "data" / "products.json"
    items = json.loads(path.read_text(encoding="utf-8"))
    for item in items:
        item["image"] = pick(item["name"], item.get("tag", ""))
        if not (ROOT / item["image"]).exists():
            item["image"] = FALLBACK.get(item.get("tag"), f"{CAT}/earbuds.jpg")
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    missing = [i["image"] for i in items if not (ROOT / i["image"]).exists()]
    print("ok", len(items), "missing files", len(missing))
    from collections import Counter
    print(Counter(i["image"] for i in items).most_common(8))


if __name__ == "__main__":
    main()
