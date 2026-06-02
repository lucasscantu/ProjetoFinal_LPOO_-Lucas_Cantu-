"""
Modelo de domínio: Usuário do sistema de acesso.

Aqui ficam concentrados dois padrões de projeto:

  * Factory Method  -> a classe ``UsuarioFactory`` decide qual subclasse
    concreta de ``Usuario`` instanciar (Aluno, Funcionario ou Visitante),
    isolando o resto do sistema dos detalhes de construção.

  * Strategy (seleção) -> cada subclasse sabe qual estratégia de validação
    de acesso deve usar, expondo o método ``get_estrategia_validacao()``.
    A regra de negócio em si vive em ``validacao_strategy.py``.

A validação de CPF (com os dois dígitos verificadores) é feita aqui, de forma
análoga à validação de placa do projeto base da locadora.
"""

from abc import ABC, abstractmethod
from enum import Enum

from .excecoes import CpfInvalidoError


class TipoUsuario(Enum):
    """Tipos de usuário aceitos pelo sistema (usado para categorização)."""
    ALUNO = "ALUNO"
    FUNCIONARIO = "FUNCIONARIO"
    VISITANTE = "VISITANTE"


class Usuario(ABC):
    """
    Classe abstrata que representa qualquer pessoa autorizada a interagir
    com as catracas. O CPF é a chave natural do usuário (equivalente à placa
    do veículo no projeto base).

    Atributos
    ---------
    cpf : str
        Identificador único, validado pelos dígitos verificadores.
    nome : str
        Nome completo do usuário.
    ativo : bool
        Indica se o cadastro está ativo (usuários inativos têm acesso negado).
    validade : date | None
        Data até a qual o acesso é válido (plano do aluno / autorização do
        visitante). Para funcionários é ``None`` (acesso sem prazo).
    """

    def __init__(self, cpf: str, nome: str, ativo: bool = True, validade=None):
        self.__cpf = ""
        self.__nome = ""
        self.cpf = cpf
        self.nome = nome
        self.ativo = ativo
        self.validade = validade

    # ------------------------------------------------------------------
    # Propriedades com validação
    # ------------------------------------------------------------------
    @property
    def cpf(self):
        return self.__cpf

    @cpf.setter
    def cpf(self, cpf: str):
        if self.valida_cpf(cpf):
            # Armazena somente os dígitos, sem pontuação
            self.__cpf = "".join(filter(str.isdigit, cpf))

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, nome: str):
        if nome is None or not nome.strip():
            raise ValueError("O nome do usuário é obrigatório!")
        self.__nome = nome.strip()

    # ------------------------------------------------------------------
    # Categorização e estratégia (polimorfismo)
    # ------------------------------------------------------------------
    @property
    @abstractmethod
    def tipo(self) -> TipoUsuario:
        """Retorna o tipo do usuário (enum TipoUsuario)."""
        pass

    @abstractmethod
    def get_estrategia_validacao(self):
        """
        Retorna a instância de ValidacaoAcessoStrategy adequada ao tipo
        do usuário. Implementa a SELEÇÃO da estratégia (padrão Strategy).
        """
        pass

    # ------------------------------------------------------------------
    # Comportamentos comuns
    # ------------------------------------------------------------------
    def exibir_dados(self) -> str:
        validade_txt = self.validade.strftime("%d/%m/%Y") if self.validade else "Sem prazo"
        return (
            f"Nome: {self.nome}\n"
            f"CPF: {self.cpf_formatado()}\n"
            f"Tipo: {self.tipo.value}\n"
            f"Ativo: {'Sim' if self.ativo else 'Não'}\n"
            f"Validade do acesso: {validade_txt}"
        )

    def cpf_formatado(self) -> str:
        """Devolve o CPF no formato 000.000.000-00 para exibição."""
        c = self.cpf
        if len(c) != 11:
            return c
        return f"{c[0:3]}.{c[3:6]}.{c[6:9]}-{c[9:11]}"

    # ------------------------------------------------------------------
    # Validação de CPF (algoritmo dos dígitos verificadores)
    # ------------------------------------------------------------------
    @staticmethod
    def valida_cpf(cpf: str) -> bool:
        """
        Valida o CPF usando o algoritmo oficial dos dois dígitos
        verificadores. Lança ``CpfInvalidoError`` quando inválido.
        """
        if cpf is None:
            raise CpfInvalidoError("CPF é obrigatório!")

        numeros = "".join(filter(str.isdigit, cpf))

        if len(numeros) != 11:
            raise CpfInvalidoError("CPF inválido! Deve conter 11 dígitos.")

        # Rejeita sequências com todos os dígitos iguais (ex.: 111.111.111-11)
        if numeros == numeros[0] * 11:
            raise CpfInvalidoError("CPF inválido! Sequência de dígitos repetidos.")

        # Cálculo do primeiro dígito verificador
        soma = sum(int(numeros[i]) * (10 - i) for i in range(9))
        resto = (soma * 10) % 11
        digito1 = 0 if resto == 10 else resto

        # Cálculo do segundo dígito verificador
        soma = sum(int(numeros[i]) * (11 - i) for i in range(10))
        resto = (soma * 10) % 11
        digito2 = 0 if resto == 10 else resto

        if digito1 != int(numeros[9]) or digito2 != int(numeros[10]):
            raise CpfInvalidoError("CPF inválido! Dígitos verificadores incorretos.")

        return True


class Aluno(Usuario):
    """
    Aluno da academia. Possui um plano com data de validade; o acesso só é
    liberado dentro do horário de funcionamento e com plano em dia.
    """

    @property
    def tipo(self) -> TipoUsuario:
        return TipoUsuario.ALUNO

    def get_estrategia_validacao(self):
        # Import local evita import circular (validacao_strategy importa o tipo)
        from .validacao_strategy import ValidacaoAlunoStrategy
        return ValidacaoAlunoStrategy()


class Funcionario(Usuario):
    """
    Funcionário do estabelecimento. Possui acesso livre (24h), bastando que
    o cadastro esteja ativo.
    """

    @property
    def tipo(self) -> TipoUsuario:
        return TipoUsuario.FUNCIONARIO

    def get_estrategia_validacao(self):
        from .validacao_strategy import ValidacaoFuncionarioStrategy
        return ValidacaoFuncionarioStrategy()


class Visitante(Usuario):
    """
    Visitante temporário. Tem acesso somente até a data de autorização e
    apenas em horário comercial.
    """

    @property
    def tipo(self) -> TipoUsuario:
        return TipoUsuario.VISITANTE

    def get_estrategia_validacao(self):
        from .validacao_strategy import ValidacaoVisitanteStrategy
        return ValidacaoVisitanteStrategy()


class UsuarioFactory:
    """
    Factory Method: centraliza a criação dos diferentes tipos de usuário.
    O resto do sistema nunca instancia Aluno/Funcionario/Visitante
    diretamente — sempre passa por aqui.
    """

    _MAPA = {
        "aluno": Aluno,
        "funcionario": Funcionario,
        "funcionário": Funcionario,
        "visitante": Visitante,
    }

    @staticmethod
    def criar_usuario(tipo: str, cpf: str, nome: str,
                      ativo: bool = True, validade=None) -> Usuario:
        chave = (tipo or "").strip().lower()
        classe = UsuarioFactory._MAPA.get(chave)
        if classe is None:
            raise ValueError(
                f"Tipo de usuário inválido: '{tipo}'. "
                f"Use 'Aluno', 'Funcionario' ou 'Visitante'."
            )
        return classe(cpf=cpf, nome=nome, ativo=ativo, validade=validade)
