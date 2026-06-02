"""
Padrão de Projeto: STRATEGY.

Cada tipo de usuário tem uma regra diferente para autorizar (ou não) a
passagem pela catraca. Em vez de espalhar ``if/elif`` por tipo pelo
controlador, encapsulamos cada regra em uma estratégia intercambiável.

A estratégia certa é escolhida polimorficamente pelo próprio usuário
(``Usuario.get_estrategia_validacao()``), e o controlador apenas chama
``validar(usuario)`` sem conhecer os detalhes de cada regra.

Cada estratégia devolve uma tupla ``(autorizado: bool, motivo: str)``.
"""

from abc import ABC, abstractmethod
from datetime import date, datetime


class ValidacaoAcessoStrategy(ABC):
    """Interface comum a todas as estratégias de validação de acesso."""

    @abstractmethod
    def validar(self, usuario) -> tuple:
        """Retorna (autorizado, motivo) para o usuário informado."""
        pass

    # Auxiliares reutilizáveis pelas estratégias concretas ----------------
    @staticmethod
    def _dentro_horario(inicio_hora: int, fim_hora: int) -> bool:
        agora = datetime.now().hour
        return inicio_hora <= agora < fim_hora

    @staticmethod
    def _validade_ok(usuario) -> bool:
        return usuario.validade is None or usuario.validade >= date.today()


class ValidacaoAlunoStrategy(ValidacaoAcessoStrategy):
    """
    Aluno: precisa estar ativo, com plano dentro da validade e o acesso
    deve ocorrer dentro do horário de funcionamento da academia (06h–23h).
    """

    HORA_ABERTURA = 6
    HORA_FECHAMENTO = 23

    def validar(self, usuario) -> tuple:
        if not usuario.ativo:
            return False, "Cadastro de aluno inativo."
        if usuario.validade is None:
            return False, "Aluno sem data de validade do plano cadastrada."
        if usuario.validade < date.today():
            return False, "Plano do aluno vencido."
        if not self._dentro_horario(self.HORA_ABERTURA, self.HORA_FECHAMENTO):
            return False, "Fora do horário de funcionamento (06h às 23h)."
        return True, "Acesso autorizado (aluno)."


class ValidacaoFuncionarioStrategy(ValidacaoAcessoStrategy):
    """
    Funcionário: acesso livre 24h, bastando que o cadastro esteja ativo.
    """

    def validar(self, usuario) -> tuple:
        if not usuario.ativo:
            return False, "Cadastro de funcionário inativo."
        return True, "Acesso autorizado (funcionário - acesso integral)."


class ValidacaoVisitanteStrategy(ValidacaoAcessoStrategy):
    """
    Visitante: precisa estar ativo, com autorização dentro da validade e
    apenas em horário comercial (08h–18h).
    """

    HORA_ABERTURA = 8
    HORA_FECHAMENTO = 18

    def validar(self, usuario) -> tuple:
        if not usuario.ativo:
            return False, "Cadastro de visitante inativo."
        if usuario.validade is None:
            return False, "Visitante sem data de autorização cadastrada."
        if usuario.validade < date.today():
            return False, "Autorização de visita expirada."
        if not self._dentro_horario(self.HORA_ABERTURA, self.HORA_FECHAMENTO):
            return False, "Visitantes só têm acesso em horário comercial (08h às 18h)."
        return True, "Acesso autorizado (visitante)."
