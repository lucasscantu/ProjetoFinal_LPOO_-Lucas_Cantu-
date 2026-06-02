"""
Sessão da aplicação — armazena o administrador autenticado durante a
execução, para que as telas possam consultar o perfil e habilitar/ocultar
opções de menu conforme as permissões.

Implementado como singleton simples a nível de módulo: importar
`sessao_atual` traz a mesma instância em qualquer ponto do sistema.
"""

from model.administrador import Administrador, PerfilAdmin


class Sessao:
    """Mantém o administrador logado durante o ciclo de vida da aplicação."""

    def __init__(self):
        self._administrador = None

    # ------------------------------------------------------------------
    def login(self, administrador: Administrador):
        if not isinstance(administrador, Administrador):
            raise TypeError("login() exige um Administrador.")
        self._administrador = administrador

    def logout(self):
        self._administrador = None

    # ------------------------------------------------------------------
    @property
    def administrador(self):
        return self._administrador

    @property
    def autenticado(self) -> bool:
        return self._administrador is not None

    @property
    def perfil(self):
        return self._administrador.perfil if self._administrador else None

    # ------------------------------------------------------------------
    def pode(self, perfil_minimo: PerfilAdmin) -> bool:
        """
        True se o administrador autenticado tem permissão para uma operação
        que exige, no mínimo, o perfil informado.

        Hierarquia: ADMIN  >  OPERADOR
        """
        if not self.autenticado:
            return False
        if perfil_minimo == PerfilAdmin.OPERADOR:
            return True   # qualquer autenticado pode (ADMIN ou OPERADOR)
        if perfil_minimo == PerfilAdmin.ADMIN:
            return self._administrador.perfil == PerfilAdmin.ADMIN
        return False

    def exigir_admin(self):
        """
        Lança PermissionError se o usuário corrente não for ADMIN.
        Usado pelos controllers para barrar operações administrativas.
        """
        if not self.pode(PerfilAdmin.ADMIN):
            raise PermissionError(
                "Operação restrita ao perfil ADMIN. "
                "Faça login com uma conta administrativa."
            )


# Instância única utilizada por toda a aplicação.
sessao_atual = Sessao()
