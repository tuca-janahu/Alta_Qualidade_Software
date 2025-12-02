from __future__ import annotations

import pytest

from src.domains.cliente import Cliente


def test_cliente_normaliza_email_corrige_arrobas_e_sufixo_com():
    c = Cliente(nome="  Ana  ", email="  ana@@petrobahia  ", cnpj="123")
    # _clean_email deve: strip, lower, trocar @@->@ e adicionar ".com" se faltar ponto no domínio
    assert c.nome == "Ana"
    assert c.email == "ana@petrobahia.com"
    assert c.cnpj == "123"


def test_cliente_email_invalido_gera_erro():
    with pytest.raises(ValueError):
        Cliente(nome="Carlos", email="sem-arroba-e-semponto", cnpj="123")

    with pytest.raises(ValueError):
        Cliente(nome="Carlos", email="", cnpj="123")

    with pytest.raises(ValueError):
        Cliente(nome="Carlos", email=None, cnpj="123")  

def test_cliente_to_storage_format_com_cnpj():
    c = Cliente(nome="Zoe", email="zoe@example.com", cnpj="123")
    assert c.to_storage_format() == "Zoe,zoe@example.com,123"

    c2 = Cliente(nome="Zoe", email="zoe@example.com", cnpj=None)
    assert c2.to_storage_format() == "Zoe,zoe@example.com,"
