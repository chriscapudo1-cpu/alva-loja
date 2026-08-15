# Liga cada produto à foto certa pelo nome.
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = "assets/img/cat"
DROP = "assets/img/drop"

# Mais específico primeiro
RULES = [
    (("condução", "ossea", "óssea"), f"{CAT}/earbuds.jpg"),
    (("gamer", "rgb"), f"{CAT}/earbuds.jpg"),
    (("esportivo gancho", "gancho"), f"{CAT}/earbuds.jpg"),
    (("fone", "tws", "headset"), f"{CAT}/earbuds.jpg"),
    (("smartwatch", "relógio quartzo", "relogio quartzo"), f"{CAT}/smartwatch.jpg"),
    (("power bank", "powerbank"), f"{CAT}/powerbank.jpg"),
    (("carregador mag", "carregador veicular", "carregador"), f"{CAT}/powerbank.jpg"),
    (("cabo", "hdmi", "hub usb", "hub mesa", "adaptador"), f"{CAT}/powerbank.jpg"),
    (("película", "pelicula", "capa iphone", "capa android", "capa de celular"), f"{CAT}/phone-case.jpg"),
    (("webcam",), f"{CAT}/webcam.jpg"),
    (("teclado",), f"{CAT}/keyboard.jpg"),
    (("mouse", "mouse pad"), f"{CAT}/keyboard.jpg"),
    (("projetor",), f"{CAT}/webcam.jpg"),
    (("anel led", "luminária anel", "luminaria anel"), f"{CAT}/mirror.jpg"),
    (("suporte mesa articulado", "suporte celular bike"), f"{CAT}/car-holder.jpg"),
    (("capa de sofá", "capa de sofa", "capa sofá", "capa sofa"), f"{CAT}/sofa.jpg"),
    (("cortina", "blackout"), f"{CAT}/sofa.jpg"),
    (("joias", "organizadora maquiagem"), f"{CAT}/jewelry.jpg"),
    (("lombar", "travesseiro", "apoio punho", "apoio pés", "apoio pes"), f"{DROP}/lombar.jpg"),
    (("umidificador",), f"{CAT}/humidifier.jpg"),
    (("fita led", "luz interna led", "luminária"), f"{CAT}/led.jpg"),
    (("relógio de parede", "relogio de parede", "relógio mesa", "relogio mesa"), f"{CAT}/smartwatch.jpg"),
    (("lixeira",), f"{CAT}/chopper.jpg"),
    (("tapete passadeira", "tapete higiênico", "tapete atividades"), f"{CAT}/yoga.jpg"),
    (("varal", "cabideiro", "gancho", "trava gaveta", "protetor de quina", "protetor tomada", "puxador"), f"{CAT}/jewelry.jpg"),
    (("caixa organizadora", "organizador geladeira", "pote hermético", "pote hermetico", "organizador temperos", "organizador mesa", "divisória", "divisoria", "pasta"), f"{CAT}/jewelry.jpg"),
    (("pano microfibra", "toalha"), f"{CAT}/yoga.jpg"),
    (("capa de fogão", "capa de fogao", "forma silicone", "luva térmica", "luva termica"), f"{CAT}/chopper.jpg"),
    (("cama caverna", "cama janela"), f"{CAT}/cat-bed.jpg"),
    (("cama ortopédica", "cama ortopedica"), f"{CAT}/dog-bed.jpg"),
    (("coleira",), f"{CAT}/collar.jpg"),
    (("guia", "peitoral", "roupa cão", "roupa cao"), f"{CAT}/collar.jpg"),
    (("comedouro", "bebedouro", "fonte água", "fonte agua"), f"{CAT}/feeder.jpg"),
    (("mordedor gelado", "babador", "chocalho"), f"{CAT}/nursing.jpg"),
    (("arranhador", "túnel", "tunel", "brinquedo laser", "brinquedo mordedor", "escova tira"), f"{CAT}/cat-bed.jpg"),
    (("bolsa transporte pet", "bolsa maternidade"), f"{CAT}/backpack.jpg"),
    (("gps pet",), f"{CAT}/smartwatch.jpg"),
    (("bolsa transversal", "bolsa shopper", "pochete", "necessaire"), f"{CAT}/bag.jpg"),
    (("mochila",), f"{CAT}/backpack.jpg"),
    (("carteira", "porta-cartão", "porta-cartao", "cinto"), f"{CAT}/wallet.jpg"),
    (("óculos", "oculos"), f"{CAT}/sunglasses.jpg"),
    (("boné", "bone", "chapéu", "chapeu"), f"{CAT}/sunglasses.jpg"),
    (("meia", "luva touch", "luva academia", "joelheira", "faixa headband", "cachecol", "lenço", "lenco"), f"{DROP}/meias.jpg"),
    (("brinco", "colar", "pulseira"), f"{CAT}/jewelry.jpg"),
    (("suporte magnético", "suporte grade", "suporte veicular", "suporte tablet encosto"), f"{CAT}/car-holder.jpg"),
    (("câmera veicular", "camera veicular", "câmera dvr", "camera dvr", "câmera de ré", "camera de re", "dash"), f"{CAT}/dashcam.jpg"),
    (("aspirador",), f"{CAT}/vacuum.jpg"),
    (("tapete borracha", "protetor sol", "capa volante"), f"{CAT}/yoga.jpg"),
    (("compressor", "inversor", "kit emergência", "kit emergencia"), f"{CAT}/vacuum.jpg"),
    (("organizador banco", "lixeira carro"), f"{CAT}/bag.jpg"),
    (("massageador de pescoço", "massageador pescoco", "massageador couro"), f"{CAT}/neck.jpg"),
    (("massageador facial", "escova facial", "removedor cravos", "spray nano"), f"{CAT}/mirror.jpg"),
    (("espelho led",), f"{CAT}/mirror.jpg"),
    (("escova alisadora", "secador", "modelador", "chapinha", "escova de dente", "kit barba", "depilador", "aparador", "lixa pé", "lixa pe", "kit manicure", "pinça"), f"{DROP}/escova.jpg"),
    (("kit skincare", "faixa skincare"), f"{CAT}/nursing.jpg"),
    (("tapete yoga", "tapete de exercício", "tapete de exercicio", "corda", "elástico", "elastico", "rolo liberação", "bola pilates", "halteres", "barra porta", "mini bike", "caneleira"), f"{CAT}/yoga.jpg"),
    (("garrafa", "cinto hidratação", "cinto hidratacao"), f"{CAT}/bag.jpg"),
    (("farol bike",), f"{CAT}/led.jpg"),
    (("aquecedor de mamadeira",), f"{CAT}/bottle-warmer.jpg"),
    (("almofada amamentação", "almofada amamentacao"), f"{CAT}/nursing.jpg"),
    (("babador", "mordedor", "chocalho", "redutor", "porta-chupeta", "escova cabelo bebê", "escova cabelo bebe"), f"{CAT}/nursing.jpg"),
    (("monitor bebê", "monitor bebe"), f"{CAT}/webcam.jpg"),
    (("cadeira alimentação", "cadeira alimentacao"), f"{CAT}/nursing.jpg"),
    (("mosquiteiro", "protetor sol carrinho", "organizador carrinho"), f"{CAT}/bag.jpg"),
    (("termômetro banho", "termometro banho", "cortador unha"), f"{CAT}/bottle-warmer.jpg"),
    (("suporte notebook", "suporte monitor"), f"{CAT}/laptop-stand.jpg"),
    (("luminária clip", "luminaria clip"), f"{CAT}/led.jpg"),
    (("etiquetadora", "grampeador", "quadro branco", "calculadora"), f"{CAT}/keyboard.jpg"),
    (("cadeira lombar",), f"{DROP}/lombar.jpg"),
    (("webcam cover",), f"{CAT}/webcam.jpg"),
    (("cabo organizador", "suporte fone mesa"), f"{CAT}/laptop-stand.jpg"),
    (("mini processador", "batedor", "grill", "cafeteira", "sifão", "sifao", "moedor", "mandoline", "escorredor", "tabua", "tábua", "descascador", "abridor", "infusor", "dispenser"), f"{CAT}/chopper.jpg"),
    (("balança", "balanca"), f"{CAT}/scale.jpg"),
    (("termômetro culinário", "termometro culinario"), f"{CAT}/scale.jpg"),
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
