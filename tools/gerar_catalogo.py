# Gera 200 produtos em 10 categorias + CSV de fornecedores AliExpress.
import csv
import json
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parents[1]
IMG = {
    "Tech": "assets/img/drop/fone.jpg",
    "Casa": "assets/img/drop/capa-sofa.jpg",
    "Pet": "assets/img/drop/cama-gato.jpg",
    "Moda": "assets/img/drop/bolsa.jpg",
    "Carro": "assets/img/drop/suporte.jpg",
    "Beleza": "assets/img/drop/pescoco.jpg",
    "Esporte": "assets/img/drop/tapete.jpg",
    "Bebê": "assets/img/drop/lombar.jpg",
    "Escritório": "assets/img/drop/joias.jpg",
    "Cozinha": "assets/img/drop/escova.jpg",
}
EXTRA = {
    "Tech": ["assets/img/drop/capa.jpg", "assets/img/drop/fone.jpg"],
    "Casa": ["assets/img/drop/lombar.jpg", "assets/img/drop/joias.jpg", "assets/img/drop/capa-sofa.jpg"],
    "Pet": ["assets/img/drop/coleira.jpg", "assets/img/drop/comedouro.jpg", "assets/img/drop/cama-gato.jpg"],
    "Moda": ["assets/img/drop/bolsa.jpg", "assets/img/drop/carteira.jpg", "assets/img/drop/meias.jpg"],
    "Carro": ["assets/img/drop/suporte.jpg", "assets/img/drop/dashcam.jpg", "assets/img/drop/aspirador.jpg"],
    "Beleza": ["assets/img/drop/pescoco.jpg", "assets/img/drop/escova.jpg"],
    "Esporte": ["assets/img/drop/tapete.jpg", "assets/img/drop/meias.jpg"],
    "Bebê": ["assets/img/drop/lombar.jpg", "assets/img/drop/cama-gato.jpg"],
    "Escritório": ["assets/img/drop/joias.jpg", "assets/img/drop/carteira.jpg"],
    "Cozinha": ["assets/img/drop/escova.jpg", "assets/img/drop/comedouro.jpg"],
}

# 20 itens por categoria: (nome, busca AliExpress, custo USD)
CATALOG = {
    "Tech": [
        ("Fone TWS Pulse", "tws earbuds bluetooth 5.3", 5.49),
        ("Fone Esportivo Gancho", "sports bluetooth earbuds hook", 6.2),
        ("Fone Gamer RGB", "gaming tws earbuds rgb", 7.4),
        ("Fone Condução Óssea", "bone conduction headphones", 14.9),
        ("Smartwatch X1", "smart watch bluetooth call", 11.8),
        ("Smartwatch Esportivo", "sport smartwatch heart rate", 13.5),
        ("Carregador Mag 15W", "magnetic wireless charger 15w", 6.8),
        ("Power Bank 20000mAh", "power bank 20000mah", 12.4),
        ("Cabo USB-C 2m", "usb c cable 2m nylon", 1.9),
        ("Hub USB-C 6 em 1", "usb c hub 6 in 1", 9.6),
        ("Capa iPhone Silicone", "iphone silicone case", 2.49),
        ("Capa Android Fosca", "android matte phone case", 2.2),
        ("Película Privacidade", "privacy screen protector", 1.8),
        ("Suporte Mesa Articulado", "desktop phone stand adjustable", 3.4),
        ("Mini Projetor Portátil", "mini portable projector", 28.0),
        ("Teclado Bluetooth Slim", "slim bluetooth keyboard", 10.5),
        ("Mouse Silencioso", "silent wireless mouse", 5.1),
        ("Webcam Full HD", "webcam 1080p autofocus", 13.2),
        ("Luminária Anel LED", "ring light 10 inch", 8.7),
        ("Adaptador HDMI 4K", "hdmi adapter 4k usb c", 4.3),
    ],
    "Casa": [
        ("Capa de Sofá 2 Lugares", "sofa cover 2 seater stretch", 7.38),
        ("Capa de Sofá 3 Lugares", "sofa cover 3 seater stretch", 8.9),
        ("Organizador de Joias", "jewelry organizer box", 8.68),
        ("Almofada Lombar", "lumbar support pillow", 12.74),
        ("Travesseiro Cervical", "cervical memory foam pillow", 11.2),
        ("Suporte Vassoura Parede", "broom holder wall mount", 5.17),
        ("Capa de Fogão", "stove burner covers", 3.17),
        ("Cortina Blackout", "blackout curtains living room", 14.5),
        ("Tapete Passadeira", "hallway runner rug", 9.8),
        ("Luminária de Mesa", "desk lamp led dimmable", 10.2),
        ("Fita LED 5m RGB", "led strip lights 5m rgb", 6.4),
        ("Umidificador 300ml", "humidifier 300ml usb", 8.1),
        ("Relógio de Parede", "modern wall clock silent", 7.6),
        ("Cabideiro de Porta", "over door hook hanger", 4.2),
        ("Caixa Organizadora", "foldable storage box", 5.9),
        ("Protetor de Quina", "corner guards baby safety", 2.8),
        ("Puxador Adesivo", "self adhesive drawer handle", 2.4),
        ("Varal Retrátil", "retractable clothes line", 6.9),
        ("Pano Microfibra Kit 10", "microfiber cleaning cloths 10", 3.5),
        ("Lixeira com Pedal", "pedal trash can 8l", 11.4),
    ],
    "Pet": [
        ("Cama Caverna Gato", "cat cave bed felt", 11.56),
        ("Cama Ortopédica Cão", "orthopedic dog bed", 18.4),
        ("Coleira LED Recarregável", "rechargeable led dog collar", 3.77),
        ("Guia Retrátil 5m", "retractable dog leash 5m", 6.2),
        ("Comedouro Lento", "slow feeder dog bowl", 7.06),
        ("Fonte Água Gato", "cat water fountain", 14.8),
        ("Arranhador Torre", "cat scratching tower", 22.0),
        ("Brinquedo Laser", "cat laser toy automatic", 5.4),
        ("Dispenser Cata-Caca", "dog poop bag dispenser", 2.1),
        ("Roupa Cão Inverno", "dog winter coat", 8.3),
        ("Peitoral Antipuxão", "no pull dog harness", 7.9),
        ("Escova Tira-Pelos", "pet hair remover brush", 4.6),
        ("Tapete Higiênico Lavável", "washable puppy pad", 9.2),
        ("Brinquedo Mordedor", "dog chew toy nylon", 3.8),
        ("Cama Janela Gato", "cat window perch", 13.1),
        ("Comedouro Elevado", "elevated dog bowl stand", 10.5),
        ("GPS Pet Mini", "mini gps pet tracker", 16.7),
        ("Túnel para Gato", "cat tunnel toy", 6.8),
        ("Bolsa Transporte Pet", "pet carrier bag airline", 15.2),
        ("Bebedouro Portátil", "portable dog water bottle", 4.9),
    ],
    "Moda": [
        ("Bolsa Transversal Mini", "mini crossbody bag", 3.78),
        ("Bolsa Shopper Couro PU", "pu leather tote bag", 9.4),
        ("Carteira Slim RFID", "rfid slim wallet", 3.98),
        ("Cinto Couro Fivela", "leather belt men", 5.6),
        ("Óculos UV400", "uv400 sunglasses", 4.2),
        ("Boné Aba Curva", "curved brim cap", 3.5),
        ("Meia Invisível Kit 5", "invisible socks 5 pairs", 3.13),
        ("Lenço Seda Cetim", "satin silk scarf", 4.8),
        ("Relógio Quartzo Pulseira", "quartz watch leather strap", 8.9),
        ("Brinco Argola Aço", "stainless hoop earrings", 2.7),
        ("Colar Corrente Fina", "thin chain necklace", 3.1),
        ("Pulseira Imã", "magnetic bracelet", 2.9),
        ("Necessaire Viagem", "travel toiletry bag", 5.2),
        ("Cinto Faixa Vestido", "women dress belt", 3.4),
        ("Chapéu Bucket", "bucket hat cotton", 4.6),
        ("Mochila Notebook 15", "laptop backpack 15 inch", 14.8),
        ("Pochete Esportiva", "running belt waist bag", 4.1),
        ("Luva Touchscreen", "touchscreen winter gloves", 5.0),
        ("Cachecol Tricot", "knit scarf unisex", 6.3),
        ("Porta-Cartão Metal", "metal card holder rfid", 3.6),
    ],
    "Carro": [
        ("Suporte Magnético Ventosa", "magnetic car phone holder suction", 1.61),
        ("Suporte Grade de Ar", "air vent phone holder", 2.4),
        ("Câmera Veicular Full HD", "dash cam 1080p", 19.83),
        ("Aspirador Portátil 120W", "portable car vacuum 120w", 20.68),
        ("Organizador Banco Traseiro", "car backseat organizer", 6.5),
        ("Carregador Veicular 45W", "car charger 45w usb c", 5.8),
        ("Câmera de Ré", "car rear view camera", 11.2),
        ("Tapete Borracha Universal", "universal car floor mat", 13.4),
        ("Protetor Sol Para-brisa", "windshield sun shade", 4.7),
        ("Aromatizador Clip", "car air freshener clip", 1.9),
        ("Kit Emergência", "car emergency kit", 12.6),
        ("Suporte Tablet Encosto", "car headrest tablet holder", 7.2),
        ("Capa Volante", "steering wheel cover", 4.4),
        ("Luz Interna LED", "car interior led light", 3.3),
        ("Compressor Mini 12V", "12v portable air compressor", 16.8),
        ("Inversor 150W", "car power inverter 150w", 14.1),
        ("Película Antiembaçante", "anti fog car film", 3.8),
        ("Gancho Encosto Kit 4", "car headrest hooks 4pcs", 2.6),
        ("Lixeira Carro Couro", "car trash bin leather", 5.5),
        ("Câmera DVR Dual", "dual dash cam front rear", 27.5),
    ],
    "Beleza": [
        ("Massageador de Pescoço", "electric neck massager", 3.08),
        ("Massageador Facial LED", "led facial massager", 9.4),
        ("Escova Alisadora", "hair straightener brush", 12.8),
        ("Secador Compacto", "travel hair dryer", 11.6),
        ("Espelho LED Maquiagem", "led makeup mirror", 10.2),
        ("Depilador Elétrico", "electric epilator women", 13.9),
        ("Kit Skincare Rolo", "jade roller gua sha set", 4.5),
        ("Aparador Pelos Nariz", "nose hair trimmer", 5.2),
        ("Escova Facial Sônica", "sonic facial cleansing brush", 7.8),
        ("Modelador Cachos", "hair curler automatic", 14.4),
        ("Removedor Cravos", "blackhead vacuum remover", 8.6),
        ("Lixa Pé Elétrica", "electric foot file", 9.1),
        ("Kit Manicure 18pç", "manicure set 18 pcs", 6.3),
        ("Chapinha Mini", "mini hair straightener", 7.1),
        ("Faixa Skincare", "skincare headband", 2.2),
        ("Organizadora Maquiagem", "makeup organizer acrylic", 9.7),
        ("Pinça LED Sobrancelha", "led eyebrow tweezers", 3.4),
        ("Spray Nano Facial", "nano facial mister", 6.8),
        ("Massageador Couro Cabeludo", "scalp massager shampoo", 3.9),
        ("Kit Barba Homem", "men beard kit trimmer", 15.2),
    ],
    "Esporte": [
        ("Tapete Yoga 6mm", "yoga mat 6mm non slip", 15.76),
        ("Tapete Yoga Extra Grosso", "thick yoga mat 10mm", 18.2),
        ("Meias Compressão 20-30", "compression socks 20-30 mmhg", 3.13),
        ("Corda Crossfit", "jump rope weighted", 4.8),
        ("Elástico Kit 5", "resistance bands set 5", 6.9),
        ("Rolo Liberação Miofascial", "foam roller massage", 8.4),
        ("Garrafa 1L Esportiva", "sports water bottle 1l", 5.6),
        ("Luvas Academia", "gym workout gloves", 4.2),
        ("Caneleira 2kg Par", "ankle weights 2kg pair", 9.5),
        ("Bola Pilates 65cm", "pilates ball 65cm", 7.7),
        ("Mini Bike Pedal", "under desk mini bike", 22.4),
        ("Suporte Celular Bike", "bike phone mount", 3.6),
        ("Farol Bike USB", "usb bike light set", 6.1),
        ("Joelheira Compressão", "knee compression sleeve", 5.4),
        ("Faixa Headband Suor", "sweat headband sport", 2.8),
        ("Cinto Hidratação", "running hydration belt", 8.2),
        ("Contador Passos Clip", "clip pedometer", 3.1),
        ("Toalha Esportiva", "microfiber sport towel", 3.9),
        ("Halteres Ajustáveis Par", "adjustable dumbbells pair", 29.0),
        ("Barra Porta Exercício", "doorway pull up bar", 16.5),
    ],
    "Bebê": [
        ("Aquecedor de Mamadeira", "baby bottle warmer portable", 10.86),
        ("Almofada Amamentação", "nursing pillow", 7.06),
        ("Babador Silicone Kit 3", "silicone baby bibs 3", 5.4),
        ("Mordedor Gelado", "teething toy freezer", 3.2),
        ("Monitor Bebê Câmera", "baby monitor camera wifi", 24.8),
        ("Protetor Tomada Kit 20", "outlet covers baby proof 20", 3.6),
        ("Trava Gaveta Kit 10", "baby drawer locks 10", 4.1),
        ("Cadeira Alimentação Portátil", "portable baby high chair", 18.9),
        ("Mosquiteiro Carrinho", "stroller mosquito net", 4.8),
        ("Organizador Carrinho", "stroller organizer bag", 7.5),
        ("Termômetro Banho", "baby bath thermometer", 5.9),
        ("Cortador Unha Bebê", "baby nail trimmer electric", 8.2),
        ("Bolsa Maternidade 3pç", "diaper bag set 3pcs", 16.4),
        ("Protetor Sol Carrinho", "stroller sun shade", 6.3),
        ("Chocalho Sensorial", "baby sensory rattle", 3.7),
        ("Tapete Atividades", "baby play mat foam", 19.2),
        ("Redutor Sanitário", "potty training seat", 6.8),
        ("Escova Cabelo Bebê", "baby hair brush set", 3.4),
        ("Porta-Chupeta Clip", "pacifier clip holder", 2.6),
        ("Umidificador Quarto Bebê", "baby room humidifier", 13.5),
    ],
    "Escritório": [
        ("Suporte Notebook Alumínio", "aluminum laptop stand", 11.8),
        ("Apoio Punho Teclado", "keyboard wrist rest", 4.6),
        ("Mouse Pad Grande", "extended gaming mouse pad", 5.9),
        ("Organizador Mesa", "desk organizer wood", 8.4),
        ("Luminária Clip LED", "clip on led desk lamp", 6.7),
        ("Suporte Monitor", "monitor riser stand", 13.2),
        ("Fone Headset Call", "office headset microphone", 12.6),
        ("Cadeira Lombar Portátil", "portable lumbar cushion office", 9.8),
        ("Divisória Gaveta", "drawer dividers adjustable", 5.2),
        ("Etiquetadora Manual", "label maker machine", 14.5),
        ("Grampeador Pesado", "heavy duty stapler", 6.1),
        ("Quadro Branco Magnético", "magnetic whiteboard small", 8.9),
        ("Cabo Organizador Kit", "cable management kit desk", 4.3),
        ("Suporte Fone Mesa", "headphone stand desk", 5.5),
        ("Calculadora Solar", "solar desk calculator", 3.8),
        ("Pasta Acordeão", "expanding file folder", 6.4),
        ("Relógio Mesa Digital", "digital desk clock", 7.2),
        ("Apoio Pés Escritório", "under desk foot rest", 10.4),
        ("Webcam Cover Kit 3", "webcam cover slider 3", 2.1),
        ("Hub Mesa Qi", "desk usb hub wireless charge", 15.6),
    ],
    "Cozinha": [
        ("Mini Processador", "mini food chopper electric", 11.4),
        ("Balança Digital 5kg", "kitchen scale 5kg", 6.8),
        ("Descascador 3 em 1", "3 in 1 peeler", 2.4),
        ("Organizador Geladeira", "fridge organizer bins", 7.9),
        ("Pote Hermético Kit 6", "airtight food containers 6", 9.6),
        ("Ralador Mandoline", "mandoline slicer", 8.2),
        ("Batedor Elétrico Mini", "mini electric whisk", 7.1),
        ("Forma Silicone Airfryer", "air fryer silicone pot", 5.8),
        ("Termômetro Culinário", "digital meat thermometer", 4.9),
        ("Abridor Elétrico", "electric can opener", 10.3),
        ("Escorredor Dobrável", "collapsible colander", 5.4),
        ("Dispenser Detergente", "soap dispenser sponge holder", 4.2),
        ("Tábua Antibacteriana", "antibacterial cutting board", 6.6),
        ("Moedor Pimenta", "pepper mill grinder", 5.1),
        ("Sifão Chantilly", "whipped cream dispenser", 13.8),
        ("Cafeteira Italiana 6x", "moka pot 6 cup", 12.2),
        ("Infusor Chá Aço", "tea infuser stainless", 3.3),
        ("Luva Térmica Silicone", "silicone oven mitts", 4.7),
        ("Organizador Temperos", "spice rack organizer", 8.5),
        ("Mini Grill Elétrico", "electric sandwich grill", 16.9),
    ],
}


def slug(text: str) -> str:
    return (
        text.lower()
        .replace("ã", "a")
        .replace("á", "a")
        .replace("â", "a")
        .replace("é", "e")
        .replace("ê", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ô", "o")
        .replace("ú", "u")
        .replace("ç", "c")
        .replace(" ", "-")
    )


def main() -> None:
    usd = 5.18
    products = []
    rows = []
    n = 0
    for cat, items in CATALOG.items():
        assert len(items) == 20, cat
        gallery = EXTRA[cat]
        for i, (name, query, usd_cost) in enumerate(items):
            n += 1
            cost = round(usd_cost * usd, 2)
            price = round(cost * 2, 2)
            url = f"https://pt.aliexpress.com/w/wholesale-{quote_plus(query)}.html"
            pid = f"{slug(cat)}-{n:03d}"
            products.append(
                {
                    "id": pid,
                    "name": name,
                    "cost": cost,
                    "price": price,
                    "image": gallery[i % len(gallery)],
                    "tag": cat,
                    "blurb": f"{cat} · envio após o pagamento. Confira variação no AliExpress.",
                    "stock": 40 + (n % 50),
                    "supplier": "AliExpress",
                    "supplierUrl": url,
                    "search": query,
                }
            )
            rows.append(
                {
                    "id": pid,
                    "categoria": cat,
                    "produto": name,
                    "custo_brl": f"{cost:.2f}".replace(".", ","),
                    "venda_brl": f"{price:.2f}".replace(".", ","),
                    "aliexpress": url,
                    "loja": f"https://alvaloja.store/produto.html?id={pid}",
                }
            )
    assert len(products) == 200
    (ROOT / "data" / "products.json").write_text(
        json.dumps(products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    csv_path = ROOT / "data" / "fornecedores.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    print(f"gerados {len(products)} produtos")
    print(csv_path)


if __name__ == "__main__":
    main()
