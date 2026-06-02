"""
Modelo de domínio: Catraca eletrônica.

A catraca usa o padrão STATE (módulo ``estados_catraca``) para controlar seu
comportamento. O código da catraca é a chave natural (ex.: "CAT-01") e é
validado de forma análoga à placa do projeto base.
"""

from .excecoes import CodigoCatracaInvalidoError
from .estados_catraca import BloqueadaState, estado_por_nome


class Catraca:
    """
    Representa um equipamento de catraca instalado em um local.

    Atributos
    ---------
    codigo : str
        Identificador único no padrão "CAT-XX" (chave natural).
    localizacao : str
        Onde a catraca está instalada (ex.: "Entrada Principal").
    estado_atual : CatracaState
        Estado corrente (Bloqueada / Liberada / Manutencao) — padrão State.
    """

    def __init__(self, codigo: str, localizacao: str, estado_nome: str = None):
        self.__codigo = ""
        self.__localizacao = ""
        self._estado_atual = None

        self.codigo = codigo
        self.localizacao = localizacao

        # Reconstrói o estado salvo no banco ou inicia em "Bloqueada".
        if estado_nome:
            self.estado_atual = estado_por_nome(self, estado_nome)
        else:
            self.estado_atual = BloqueadaState(self)

    # ------------------------------------------------------------------
    # Propriedades
    # ------------------------------------------------------------------
    @property
    def codigo(self):
        return self.__codigo

    @codigo.setter
    def codigo(self, codigo: str):
        if self.valida_codigo(codigo):
            self.__codigo = codigo.strip().upper()

    @property
    def localizacao(self):
        return self.__localizacao

    @localizacao.setter
    def localizacao(self, localizacao: str):
        if localizacao is None or not localizacao.strip():
            raise ValueError("A localização da catraca é obrigatória!")
        self.__localizacao = localizacao.strip()

    @property
    def estado_atual(self):
        return self._estado_atual

    @estado_atual.setter
    def estado_atual(self, novo_estado):
        self._estado_atual = novo_estado

    # ------------------------------------------------------------------
    # Operações que delegam ao estado atual (padrão State)
    # ------------------------------------------------------------------
    def liberar(self):
        self.estado_atual.liberar()

    def bloquear(self):
        self.estado_atual.bloquear()

    def enviar_manutencao(self):
        self.estado_atual.enviar_manutencao()

    def nome_estado(self) -> str:
        return self.estado_atual.nome()

    def esta_em_manutencao(self) -> bool:
        return self.nome_estado() == "Manutencao"

    # ------------------------------------------------------------------
    # Exibição
    # ------------------------------------------------------------------
    def exibir_dados(self) -> str:
        return (
            f"Código: {self.codigo}\n"
            f"Localização: {self.localizacao}\n"
            f"Estado atual: {self.nome_estado()}"
        )

    # ------------------------------------------------------------------
    # Validação do código
    # ------------------------------------------------------------------
    @staticmethod
    def valida_codigo(codigo: str) -> bool:
        """
        Valida o código no padrão 'CAT-' seguido de 1 a 3 dígitos.
        Ex.: CAT-1, CAT-01, CAT-123.
        """
        if codigo is None or not codigo.strip():
            raise CodigoCatracaInvalidoError("O código da catraca é obrigatório!")

        c = codigo.strip().upper()
        if not c.startswith("CAT-"):
            raise CodigoCatracaInvalidoError(
                "Código inválido! Deve começar com 'CAT-' (ex.: CAT-01)."
            )

        sufixo = c[4:]
        if not sufixo.isdigit() or not (1 <= len(sufixo) <= 3):
            raise CodigoCatracaInvalidoError(
                "Código inválido! Após 'CAT-' deve haver de 1 a 3 dígitos (ex.: CAT-01)."
            )
        return True
