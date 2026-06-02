"""
Entidade Administrador — representa um operador do sistema (não o usuário
físico que passa pela catraca; esses estão em model.usuario).

Define o conceito de PERFIL/papel de acesso (Role):
    ADMIN     -> acesso total (cadastros + operação + gerência de admins)
    OPERADOR  -> apenas operações cotidianas (simular acesso + histórico)

A senha é armazenada como hash SHA-256 (hex) — nunca em texto puro.
"""
import hashlib
from enum import Enum


class PerfilAdmin(Enum):
    """Perfis de acesso possíveis para um administrador do sistema."""
    ADMIN = "ADMIN"
    OPERADOR = "OPERADOR"

    @property
    def descricao(self):
        return {
            "ADMIN":    "Administrador",
            "OPERADOR": "Operador",
        }[self.value]


class Administrador:
    """Operador autenticável do sistema, com um perfil de acesso."""

    def __init__(self, login, nome, perfil, ativo=True, id_=None, senha_hash=None):
        self._id = id_
        self.login = login
        self.nome = nome
        self.perfil = perfil if isinstance(perfil, PerfilAdmin) else PerfilAdmin(perfil)
        self.ativo = ativo
        self.senha_hash = senha_hash  # já em hash; nunca recebe texto puro

    # ------------------------------------------------------------------
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, valor):
        self._id = valor

    # ------------------------------------------------------------------
    @staticmethod
    def hash_senha(senha_texto: str) -> str:
        """Calcula o hash SHA-256 (hex) de uma senha em texto puro."""
        if senha_texto is None:
            senha_texto = ""
        return hashlib.sha256(senha_texto.encode("utf-8")).hexdigest()

    def verificar_senha(self, senha_texto: str) -> bool:
        """True se o hash da senha informada bate com o armazenado."""
        if not self.senha_hash:
            return False
        return self.hash_senha(senha_texto) == self.senha_hash

    # ------------------------------------------------------------------
    def is_admin(self) -> bool:
        return self.perfil == PerfilAdmin.ADMIN

    def is_operador(self) -> bool:
        return self.perfil == PerfilAdmin.OPERADOR

    def exibir_dados(self) -> str:
        return (
            f"Login:  {self.login}\n"
            f"Nome:   {self.nome}\n"
            f"Perfil: {self.perfil.descricao}\n"
            f"Ativo:  {'Sim' if self.ativo else 'Não'}"
        )

    def __repr__(self):
        return f"Administrador(login={self.login!r}, perfil={self.perfil.value})"
