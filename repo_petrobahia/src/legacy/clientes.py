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
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


# 1) ENTIDADE

@dataclass(slots=True)
class Cliente:
    """Entidade Cliente com validação ao construir."""
    nome: str
    email: str

    def __post_init__(self) -> None:
        if not self.nome or not self.nome.strip():
            raise ValueError("O nome do cliente não pode estar em branco.")

        cleaned = self._clean_email(self.email)
        if not self._validate_email(cleaned):
            raise ValueError(f"Formato de email inválido: {self.email!r}")

        # normaliza
        self.nome = self.nome.strip()
        self.email = cleaned

    @staticmethod
    def _clean_email(email: str) -> str:
        if not isinstance(email, str):
            return ""
        return email.strip().lower().replace("@@", "@")

    @staticmethod
    def _validate_email(email: str) -> bool:
        return bool(EMAIL_REGEX.match(email))

    def to_storage_format(self) -> str:
        return f"{self.nome},{self.email}"


# 2) PORTAS (Protocol) + ADAPTERS

class ClienteRepository(Protocol):
    """Porta de persistência (abstração)."""
    def save(self, cliente: Cliente) -> None: ...


class FileClienteRepository:
    """Repositório baseado em arquivo texto (adapter)."""
    def __init__(self, path: Path | str = "clientes.txt") -> None:
        self.path = Path(path)

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
    repository: ClienteRepository,
    notifier: NotificationService,
) -> Cliente:

    cliente = Cliente(nome, email)
    repository.save(cliente)
    notifier.send_welcome_email(cliente)
    logging.info("Cliente cadastrado: %s <%s>", cliente.nome, cliente.email)
    return cliente
    