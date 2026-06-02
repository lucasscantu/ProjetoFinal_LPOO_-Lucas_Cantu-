"""
Modelo de domínio: Acesso (registro de passagem).

É a ENTIDADE ASSOCIATIVA que materializa o relacionamento N–N entre
``Usuario`` e ``Catraca``: um usuário passa por várias catracas ao longo do
tempo, e cada catraca registra a passagem de vários usuários. Cada registro
guarda quando ocorreu, o sentido (entrada/saída), se foi autorizado e o
motivo (quando negado).
"""

from datetime import datetime
from enum import Enum

from .usuario import Usuario
from .catraca import Catraca


class TipoAcesso(Enum):
    """Sentido da passagem pela catraca."""
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"


class Acesso:
    """
    Registro de uma tentativa de passagem por uma catraca.

    Atributos
    ---------
    usuario : Usuario
        Quem tentou passar.
    catraca : Catraca
        Onde a passagem foi tentada.
    tipo : TipoAcesso
        ENTRADA ou SAIDA.
    autorizado : bool
        Resultado da validação (Strategy).
    motivo : str
        Justificativa do resultado (especialmente útil quando negado).
    data_hora : datetime
        Momento do registro.
    id : int | None
        Chave primária (atribuída pelo banco).
    """

    def __init__(self,
                 usuario: Usuario,
                 catraca: Catraca,
                 tipo: TipoAcesso = TipoAcesso.ENTRADA,
                 autorizado: bool = False,
                 motivo: str = "",
                 data_hora: datetime = None,
                 id_acesso: int = None):
        self.id = id_acesso
        self.usuario = usuario
        self.catraca = catraca
        self.tipo = tipo
        self.autorizado = autorizado
        self.motivo = motivo
        self.data_hora = data_hora if data_hora is not None else datetime.now()

    # ------------------------------------------------------------------
    # Propriedades com validação
    # ------------------------------------------------------------------
    @property
    def usuario(self):
        return self.__usuario

    @usuario.setter
    def usuario(self, obj):
        if obj is None:
            raise ValueError("O acesso precisa estar vinculado a um usuário.")
        self.__usuario = obj

    @property
    def catraca(self):
        return self.__catraca

    @catraca.setter
    def catraca(self, obj):
        if obj is None:
            raise ValueError("O acesso precisa estar vinculado a uma catraca.")
        self.__catraca = obj

    @property
    def tipo(self):
        return self.__tipo

    @tipo.setter
    def tipo(self, valor):
        if isinstance(valor, TipoAcesso):
            self.__tipo = valor
        elif isinstance(valor, str):
            try:
                self.__tipo = TipoAcesso(valor.upper())
            except ValueError:
                raise ValueError(f"Tipo de acesso inválido: {valor}")
        else:
            raise ValueError("Tipo de acesso deve ser TipoAcesso ou string.")

    # ------------------------------------------------------------------
    # Exibição
    # ------------------------------------------------------------------
    def exibir_dados(self) -> str:
        return (
            f"ID: {self.id}\n"
            f"Usuário: {self.usuario.nome} ({self.usuario.cpf_formatado()})\n"
            f"Catraca: {self.catraca.codigo} - {self.catraca.localizacao}\n"
            f"Sentido: {self.tipo.value}\n"
            f"Data/Hora: {self.data_hora.strftime('%d/%m/%Y %H:%M:%S')}\n"
            f"Resultado: {'AUTORIZADO' if self.autorizado else 'NEGADO'}\n"
            f"Motivo: {self.motivo}"
        )
