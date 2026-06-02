"""
Padrão de Projeto: STATE.

Modela o comportamento físico de uma catraca eletrônica, que muda de
comportamento conforme seu estado interno. É o mesmo padrão usado pelo
projeto base da locadora (estados do veículo), aqui aplicado às catracas:

    BloqueadaState  -> estado padrão; trava fechada aguardando autorização.
    LiberadaState   -> destravada momentaneamente para a passagem autorizada.
    ManutencaoState -> fora de operação; nenhuma passagem é permitida.

Cada estado concreto sabe responder às três operações da catraca
(``liberar``, ``bloquear``, ``enviar_manutencao``) e é responsável por
disparar a transição para o próximo estado quando a operação é válida.
"""

from abc import ABC, abstractmethod

from .excecoes import TransicaoEstadoInvalidaError


class CatracaState(ABC):
    """Interface comum a todos os estados da catraca."""

    def __init__(self, catraca):
        self.catraca = catraca

    @property
    def catraca(self):
        return self.__catraca

    @catraca.setter
    def catraca(self, valor):
        self.__catraca = valor

    @abstractmethod
    def liberar(self):
        """Destrava a catraca para uma passagem autorizada."""
        pass

    @abstractmethod
    def bloquear(self):
        """Trava a catraca (estado de repouso)."""
        pass

    @abstractmethod
    def enviar_manutencao(self):
        """Coloca a catraca em manutenção (fora de operação)."""
        pass

    def nome(self) -> str:
        """Nome curto do estado, usado para persistência e exibição."""
        return self.__class__.__name__.replace("State", "")


class BloqueadaState(CatracaState):
    """Estado de repouso: a catraca está travada aguardando autorização."""

    def liberar(self):
        # Import tardio para evitar dependência circular entre os estados
        self.catraca.estado_atual = LiberadaState(self.catraca)

    def bloquear(self):
        # Já está bloqueada — operação idempotente, sem transição.
        pass

    def enviar_manutencao(self):
        self.catraca.estado_atual = ManutencaoState(self.catraca)


class LiberadaState(CatracaState):
    """Estado momentâneo: a catraca está destravada para a passagem."""

    def liberar(self):
        # Já liberada; não faz nada.
        pass

    def bloquear(self):
        # Após a passagem, a catraca volta a travar (comportamento físico real).
        self.catraca.estado_atual = BloqueadaState(self.catraca)

    def enviar_manutencao(self):
        raise TransicaoEstadoInvalidaError(
            "Não é possível enviar para manutenção com a catraca liberada. "
            "Conclua/cancele a passagem primeiro."
        )


class ManutencaoState(CatracaState):
    """Estado fora de operação: nenhuma passagem é permitida."""

    def liberar(self):
        raise TransicaoEstadoInvalidaError(
            "Catraca em manutenção: não é possível liberar a passagem."
        )

    def bloquear(self):
        # Sair da manutenção devolve a catraca ao estado de repouso.
        self.catraca.estado_atual = BloqueadaState(self.catraca)

    def enviar_manutencao(self):
        # Já está em manutenção.
        pass


# Tabela auxiliar para reconstruir o estado a partir do nome salvo no banco.
MAPA_ESTADOS = {
    "Bloqueada": BloqueadaState,
    "Liberada": LiberadaState,
    "Manutencao": ManutencaoState,
}


def estado_por_nome(catraca, nome: str) -> CatracaState:
    """Recria a instância de estado correta a partir do nome persistido."""
    classe = MAPA_ESTADOS.get(nome, BloqueadaState)
    return classe(catraca)
