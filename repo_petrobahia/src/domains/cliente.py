"""
Entidade Cliente (separada para seguir PEP8 e SOLID).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


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
