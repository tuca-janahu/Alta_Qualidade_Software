from __future__ import annotations

from decimal import Decimal

from src.domains.pedido import Pedido, Produto
from src.services.preco_calculadora import processar_pedido


def test_pedido_diesel_com_mega10_e_arredondamento_zero_casas():
    pedido = Pedido(cliente="TransLog", produto=Produto.DIESEL, qtd=1200, cupom="MEGA10")
    total = processar_pedido(pedido)
    # 3.99*1200 = 4788; >1000 => 10% off => 4309.2; MEGA10 => 3878.28; round 0 (half up) => 3878
    assert total == Decimal("3878")


def test_pedido_gasolina_mais_de_200_sem_cupom():
    pedido = Pedido(cliente="MoveMais", produto=Produto.GASOLINA, qtd=300, cupom=None)
    total = processar_pedido(pedido)
    # 5.19*300 = 1557; >200 => -100 => 1457; round(2) => 1457.00
    assert total == Decimal("1457.00")


def test_pedido_etanol_com_novo5_e_truncamento():
    pedido = Pedido(cliente="EcoFrota", produto=Produto.ETANOL, qtd=90, cupom="NOVO5")
    total = processar_pedido(pedido)
    # Base: 3.59*90 = 323.10; >80 => *0.97 = 313.407; NOVO5 => *0.95 = 297.73665
    # Outros => truncar para 2 casas => 297.73
    assert total == Decimal("297.73")


def test_pedido_lubrificante_com_lub2():
    pedido = Pedido(cliente="PetroPark", produto=Produto.LUBRIFICANTE, qtd=12, cupom="LUB2")
    total = processar_pedido(pedido)
    # 25*12 = 300; LUB2 => -2 => 298; truncar(2) => 298.00
    assert total == Decimal("298.00")


def test_qtd_zero_retorna_zero():
    pedido = Pedido(cliente="Zero", produto=Produto.ETANOL, qtd=0, cupom=None)
    total = processar_pedido(pedido)
    assert total == Decimal("0")
