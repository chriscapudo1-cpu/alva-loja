"""Gera descrição e a foto principal de cada produto (sem galeria extra)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "products.json"
ALI = ROOT / "assets" / "img" / "ali"

LEDE = {
    "Tech": "Eletrônico compacto para o dia a dia, sem excesso de função.",
    "Casa": "Peça para organizar ou completar a casa com pouco esforço.",
    "Pet": "Acessório pensado para o conforto e a rotina do animal.",
    "Moda": "Complemento de uso frequente, fácil de combinar.",
    "Carro": "Acessório para o carro: instalação simples e uso imediato.",
    "Beleza": "Item de cuidado pessoal para a rotina em casa.",
    "Esporte": "Equipamento para treino em casa, academia ou ar livre.",
    "Bebê": "Peça para o dia a dia com o bebê, escolhida pelo uso prático.",
    "Escritório": "Objeto de mesa ou arquivo para o trabalho ficar mais limpo.",
    "Cozinha": "Utensílio de cozinha para preparar, guardar ou servir.",
}

HINTS = [
    (("bluetooth", "tws", "wireless", "sem fio"), "Conexão sem fio, sem enrolar cabo."),
    (("usb-c", "usb c", "type-c"), "Saída ou recarga em USB-C."),
    (("led", "rgb"), "Tem iluminação LED para uso à noite ou detalhe visual."),
    (("inox", "stainless", "aço"), "Acabamento em aço inox, mais fácil de limpar."),
    (("silicone",), "Toque em silicone, macio e fácil de lavar."),
    (("impermeável", "waterproof", "water"), "Melhor resistência à água no uso diário."),
    (("ajustável", "adjustable"), "Tamanho ou ângulo ajustável."),
    (("portátil", "portable", "mini", "viagem", "travel"), "Formato compacto para levar na bolsa."),
    (("recarregável", "rechargeable"), "Recarregável, sem ficar trocando pilha."),
    (("kit", "pack", "par", "set"), "Vai em conjunto, pronto para usar."),
]


def cover_for(item: dict) -> str:
    pid = item["id"]
    main = item.get("image") or f"assets/img/ali/{pid}.jpg"
    path = ALI / f"{pid}.jpg"
    if path.exists() and path.stat().st_size > 4000:
        return f"assets/img/ali/{pid}.jpg"
    return main


def describe(item: dict) -> str:
    tag = item.get("tag") or ""
    name = item["name"]
    hay = f"{name} {item.get('search') or ''}".lower()
    bits = [LEDE.get(tag, "Objeto escolhido para o dia a dia.")]
    for keys, line in HINTS:
        if any(k in hay for k in keys):
            bits.append(line)
        if len(bits) == 3:
            break
    bits.append(
        f"O {name} sai da ALVA após a confirmação do pagamento. "
        "Confira a foto e os detalhes antes de colocar na sacola."
    )
    return " ".join(bits)


def main() -> None:
    products = json.loads(SRC.read_text(encoding="utf-8"))
    for item in products:
        cover = cover_for(item)
        item["image"] = cover
        item["images"] = [cover]
        item["description"] = describe(item)
    SRC.write_text(json.dumps(products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(products)} produtos · só a foto principal")


if __name__ == "__main__":
    main()
