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
    cnpj: str | None = None


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
        """
            Normaliza e corrige pequenos erros comuns:
            - remove espaços e baixa caixa
            - troca '@@' por '@'
            - se houver '@' mas o domínio não tiver '.', acrescenta '.com'
        """
        
        if not isinstance(email, str):
            return ""
        email_limpo = email.strip().lower().replace("@@", "@")

        # Se tem '@' e o domínio não contém '.', acrescenta '.com'
        if "@" in email_limpo:
            local, domain = email_limpo.split("@", 1)
            if domain and "." not in domain:
                domain = domain + ".com"
                email_limpo = f"{local}@{domain}"

        return email_limpo

    @staticmethod
    def _validate_email(email: str) -> bool:
        return bool(EMAIL_REGEX.match(email))

    def to_storage_format(self) -> str:
        return f"{self.nome},{self.email},{self.cnpj or ''}"
