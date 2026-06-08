from dao.catraca_dao import CatracaDAO
from model.catraca import Catraca
from model.excecoes import CodigoCatracaInvalidoError, TransicaoEstadoInvalidaError


class CatracaController:
    """
    Controlador da entidade Catraca. Além do CRUD, expõe operações que
    disparam transições de estado (padrão State) e as persistem.
    """

    def __init__(self):
        self.catraca_dao = CatracaDAO()

    # ------------------------------------------------------------------
    def salvar_catraca(self, codigo, localizacao):
        if not codigo or not localizacao:
            return False, "Preencha o código e a localização."
        try:
            if self.catraca_dao.buscar_por_codigo(codigo):
                return False, f"Já existe catraca com o código {codigo.upper()}."
            nova = Catraca(codigo=codigo, localizacao=localizacao)
            return self.catraca_dao.salvar(nova)
        except CodigoCatracaInvalidoError as e:
            return False, str(e)
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {e}"

    def atualizar_catraca(self, codigo, localizacao):
        if not codigo or not localizacao:
            return False, "Preencha o código e a localização."
        try:
            existente = self.catraca_dao.buscar_por_codigo(codigo)
            if not existente:
                return False, f"Catraca {codigo.upper()} não encontrada."
            # Mantém o estado atual e troca apenas a localização
            existente.localizacao = localizacao
            return self.catraca_dao.atualizar(existente)
        except Exception as e:
            return False, f"Erro inesperado: {e}"

    def remover_catraca(self, codigo):
        if not codigo:
            return False, "Código não informado."
        try:
            return self.catraca_dao.remover(codigo)
        except Exception as e:
            return False, f"Erro inesperado: {e}"

    def listar_catracas(self):
        try:
            return self.catraca_dao.listar_todos()
        except Exception as e:
            print(f"Erro ao listar catracas: {e}")
            return None

    def buscar_por_codigo(self, codigo):
        try:
            return self.catraca_dao.buscar_por_codigo(codigo)
        except Exception as e:
            print(f"Erro ao buscar catraca: {e}")
            return None

    # ------------------------------------------------------------------
    # Operações de mudança de estado (padrão State)
    # ------------------------------------------------------------------
    def alternar_manutencao(self, codigo):
        """
        Coloca a catraca em manutenção ou a retira da manutenção,
        persistindo o novo estado.
        """
        try:
            catraca = self.catraca_dao.buscar_por_codigo(codigo)
            if not catraca:
                return False, "Catraca não encontrada."

            if catraca.esta_em_manutencao():
                catraca.bloquear()  # sai da manutenção -> Bloqueada
                msg = f"Catraca {catraca.codigo} retirada da manutenção."
            else:
                catraca.enviar_manutencao()  # entra em manutenção
                msg = f"Catraca {catraca.codigo} enviada para manutenção."

            ok, _ = self.catraca_dao.atualizar(catraca)
            if not ok:
                return False, "Falha ao persistir o novo estado da catraca."
            return True, msg

        except TransicaoEstadoInvalidaError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {e}"
