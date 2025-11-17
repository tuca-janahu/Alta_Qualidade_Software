from __future__ import annotations

import logging
from decimal import Decimal

from src.services.preco_calculadora import processar_pedido
from src.services.servico_cliente import (
    FileClienteRepository,
    ConsoleNotificationService,
    cadastrar_cliente,
)
from src.domains.pedido import Pedido, Produto  

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

pedidos = [
    {"cliente": "TransLog", "produto": "diesel", "qtd": 1200, "cupom": "MEGA10"},
    {"cliente": "MoveMais", "produto": "gasolina", "qtd": 300, "cupom": None},
    {"cliente": "EcoFrota", "produto": "etanol", "qtd": 50, "cupom": "NOVO5"},
    {"cliente": "PetroPark", "produto": "lubrificante", "qtd": 12, "cupom": "LUB2"},
]

clientes = [
    {"nome": "Ana Paula", "email": "ana@@petrobahia", "cnpj": "123"},
    {"nome": "Carlos", "email": "carlos@petrobahia.com", "cnpj": "456"},
]

def run() -> None:
    print("==== Início processamento PetroBahia ====")

    repo = FileClienteRepository("clientes.txt")
    notifier = ConsoleNotificationService()

    # ✅ chama com (nome, email, repo, notifier)
    for c in clientes:
        try:
            cadastrar_cliente(c["nome"], c["email"], c.get("cnpj"), repo, notifier)
            print("cliente ok:", c["nome"])
        except Exception as exc:
            print("cliente com problema:", c, f"— {exc}")

    valores: list[Decimal] = []
    for p in pedidos:
        pedido = Pedido(
            cliente=p["cliente"],
            produto=Produto(p["produto"]),
            qtd=int(p["qtd"]),
            cupom=p.get("cupom"),
        )
        valor_final = processar_pedido(pedido)
        valores.append(valor_final)
        print("pedido:", p, "-- valor final:", valor_final)

    print("TOTAL =", sum(valores))
    print("==== Fim processamento PetroBahia ====")

if __name__ == "__main__":
    run()
