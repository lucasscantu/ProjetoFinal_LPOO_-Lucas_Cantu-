"""
Exceções personalizadas do Sistema de Catraca Eletrônica.

Centralizar as exceções em um único módulo facilita o tratamento de erros
nas camadas de controle e de interface gráfica, mantendo as mensagens
consistentes em toda a aplicação.
"""


class CpfInvalidoError(Exception):
    """Disparada quando o CPF informado não passa na validação."""
    pass


class CodigoCatracaInvalidoError(Exception):
    """Disparada quando o código da catraca está fora do padrão esperado."""
    pass


class DataInvalidaError(Exception):
    """Disparada quando uma data informada é inválida ou incoerente."""
    pass


class TransicaoEstadoInvalidaError(Exception):
    """Disparada quando se tenta uma transição de estado não permitida na catraca."""
    pass
