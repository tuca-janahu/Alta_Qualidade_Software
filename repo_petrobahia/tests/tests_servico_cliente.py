from __future__ import annotations

from pathlib import Path

from src.domains.cliente import Cliente
from src.services.servico_cliente import (
    ClienteRepository,
    FileClienteRepository,
    NotificationService,
    cadastrar_cliente,
)


class RepoStub(ClienteRepository):  # type: ignore[misc]
    def __init__(self) -> None:
        self.saved: list[Cliente] = []

    def save(self, cliente: Cliente) -> None:
        self.saved.append(cliente)


class NotifierStub(NotificationService):  # type: ignore[misc]
    def __init__(self) -> None:
        self.sent_to: list[str] = []

    def send_welcome_email(self, cliente: Cliente) -> None:
        self.sent_to.append(cliente.email)


def test_cadastrar_cliente_orquestra_fluxo_ok():
    repo = RepoStub()
    notifier = NotifierStub()

    cliente = cadastrar_cliente("Ana", "ana@@petrobahia", "123", repo, notifier)
    assert cliente.email == "ana@petrobahia.com"
    assert repo.saved and repo.saved[0] is cliente
    assert notifier.sent_to == [cliente.email]


def test_file_cliente_repository_salva_em_arquivo_temporario(tmp_path: Path):
    destino = tmp_path / "clientes.txt"
    repo = FileClienteRepository(path=destino)

    cliente_teste = Cliente("Bob", "bob@example.com", "456")
    repo.save(cliente_teste)

    assert destino.exists()
    content = destino.read_text(encoding="utf-8").strip().splitlines()
    assert content == ["Bob,bob@example.com,456"]
