from datetime import datetime

from dao.acesso_dao import AcessoDAO
from dao.usuario_dao import UsuarioDAO
from dao.catraca_dao import CatracaDAO
from model.acesso import Acesso, TipoAcesso


class AcessoController:
    """
    Controlador dos acessos. É aqui que os dois padrões comportamentais se
    encontram na operação principal do sistema (``processar_acesso``):

      1. STATE   -> se a catraca está em manutenção, a passagem é barrada de
                    imediato; quando autorizada, a catraca é liberada e
                    re-bloqueada (simulando a passagem física).
      2. STRATEGY-> a regra de autorização varia conforme o tipo de usuário
                    (a estratégia é obtida do próprio usuário).

    O resultado (autorizado/negado + motivo) é sempre registrado como um
    objeto Acesso no banco — inclusive as tentativas negadas, para auditoria.
    """

    def __init__(self):
        self.acesso_dao = AcessoDAO()
        self.usuario_dao = UsuarioDAO()
        self.catraca_dao = CatracaDAO()

    # ------------------------------------------------------------------
    def processar_acesso(self, cpf, codigo_catraca, tipo_str):
        """
        Processa uma tentativa de passagem.

        Retorna (autorizado: bool, mensagem: str).
        """
        if not cpf or not codigo_catraca:
            return False, "Selecione o usuário e a catraca."

        try:
            usuario = self.usuario_dao.buscar_por_cpf(cpf)
            if not usuario:
                return False, "Usuário não encontrado."

            catraca = self.catraca_dao.buscar_por_codigo(codigo_catraca)
            if not catraca:
                return False, "Catraca não encontrada."

            tipo = TipoAcesso(tipo_str.upper()) if tipo_str else TipoAcesso.ENTRADA

            # --- (1) STATE: catraca em manutenção bloqueia tudo -----------
            if catraca.esta_em_manutencao():
                motivo = "Catraca em manutenção — fora de operação."
                self._registrar(usuario, catraca, tipo, False, motivo)
                return False, motivo

            # --- (2) STRATEGY: regra de autorização por tipo de usuário ---
            estrategia = usuario.get_estrategia_validacao()
            autorizado, motivo = estrategia.validar(usuario)

            # --- (1) STATE: efetua a passagem física quando autorizado ----
            if autorizado:
                catraca.liberar()              # Bloqueada -> Liberada
                catraca.bloquear()             # Liberada  -> Bloqueada (re-trava)
                self.catraca_dao.atualizar(catraca)

            self._registrar(usuario, catraca, tipo, autorizado, motivo)
            return autorizado, motivo

        except Exception as e:
            return False, f"Erro ao processar acesso: {e}"

    def _registrar(self, usuario, catraca, tipo, autorizado, motivo):
        acesso = Acesso(
            usuario=usuario,
            catraca=catraca,
            tipo=tipo,
            autorizado=autorizado,
            motivo=motivo,
            data_hora=datetime.now(),
        )
        self.acesso_dao.salvar(acesso)

    # ------------------------------------------------------------------
    # Consultas / administração do histórico
    # ------------------------------------------------------------------
    def listar_acessos(self):
        try:
            return self.acesso_dao.listar_todos()
        except Exception as e:
            print(f"Erro ao listar acessos: {e}")
            return []

    def filtrar_acessos(self, resultado="TODOS", cpf=""):
        try:
            return self.acesso_dao.listar_filtrado(resultado, cpf)
        except Exception as e:
            print(f"Erro ao filtrar acessos: {e}")
            return []

    def remover_acesso(self, id_acesso):
        try:
            return self.acesso_dao.remover(id_acesso)
        except Exception as e:
            return False, f"Erro inesperado: {e}"
