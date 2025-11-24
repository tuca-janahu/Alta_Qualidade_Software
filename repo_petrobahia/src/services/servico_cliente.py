"""
Módulo de lógica de Clientes.

Contém:
- Cliente: entidade com validação própria.
- ClienteRepository (Protocol) + FileClienteRepository: persistência.
- NotificationService (Protocol) + ConsoleNotificationService: notificação.
- cadastrar_cliente: caso de uso com injeção de dependências.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Protocol

from ..domains.cliente import Cliente


# 2) PORTAS (Protocol) + ADAPTERS
class ClienteRepository(Protocol):
    """Porta de persistência (abstração)."""
    def save(self, cliente: Cliente) -> None: ...


class FileClienteRepository:
    """Salva em <src>/clientes.txt por padrão."""
    def __init__(self, path: str | Path | None = None) -> None:
        default_path = Path(__file__).resolve().parents[1] / "clientes.txt"
        self.path = Path(path) if path else default_path

    def save(self, cliente: Cliente) -> None:
        try:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(cliente.to_storage_format() + "\n")
        except OSError as exc:
            raise IOError(f"Falha ao salvar em {self.path}") from exc

class NotificationService(Protocol):
    """Porta de notificação (abstração)."""
    def send_welcome_email(self, cliente: Cliente) -> None: ...


class ConsoleNotificationService:
    """Notificação de exemplo (adapter)."""
    def send_welcome_email(self, cliente: Cliente) -> None:
        logging.info("Enviando e-mail de boas-vindas para %s", cliente.email)


# 3) CASO DE USO
def cadastrar_cliente(
    nome: str,
    email: str,
    cnpj: str | None,
    repository: ClienteRepository,
    notifier: NotificationService,
) -> Cliente:
    """
    Orquestra o cadastro: valida, persiste e notifica.
    Lança ValueError para dados inválidos e IOError para falha de I/O.
    """

    cliente = Cliente(nome, email, cnpj)
    repository.save(cliente)
    notifier.send_welcome_email(cliente)
    logging.info("Cliente cadastrado: %s <%s> (%s)", cliente.nome, cliente.email, cliente.cnpj)
    return cliente
