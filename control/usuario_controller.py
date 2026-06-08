from datetime import datetime

from dao.usuario_dao import UsuarioDAO
from model.usuario import UsuarioFactory
from model.excecoes import CpfInvalidoError


class UsuarioController:
    """
    Controlador da entidade Usuario. Valida os dados vindos da tela e delega
    a persistência ao DAO. Sempre devolve a dupla (sucesso: bool, msg: str)
    ou listas de objetos, conforme o caso.
    """

    def __init__(self):
        self.usuario_dao = UsuarioDAO()

    # ------------------------------------------------------------------
    @staticmethod
    def _converter_validade(validade_str: str, tipo: str):
        """
        Converte a string 'dd/mm/aaaa' em date. Para funcionário a validade
        é opcional (None). Para aluno/visitante é obrigatória.
        """
        validade_str = (validade_str or "").strip()
        tipo_low = tipo.strip().lower()

        if not validade_str:
            if tipo_low.startswith("funcion"):
                return None
            raise ValueError("A data de validade é obrigatória para este tipo de usuário.")

        try:
            return datetime.strptime(validade_str, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Data de validade inválida. Use o formato dd/mm/aaaa.")

    # ------------------------------------------------------------------
    def salvar_usuario(self, cpf, nome, tipo, ativo, validade_str):
        if not cpf or not nome or not tipo:
            return False, "Preencha CPF, nome e tipo."

        try:
            validade = self._converter_validade(validade_str, tipo)

            if self.usuario_dao.buscar_por_cpf(cpf):
                return False, f"Já existe usuário cadastrado com o CPF {cpf}."

            novo = UsuarioFactory.criar_usuario(
                tipo=tipo, cpf=cpf, nome=nome, ativo=ativo, validade=validade
            )
            return self.usuario_dao.salvar(novo)

        except CpfInvalidoError as e:
            return False, str(e)
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {e}"

    def atualizar_usuario(self, cpf, nome, tipo, ativo, validade_str):
        if not cpf or not nome or not tipo:
            return False, "Preencha CPF, nome e tipo."

        try:
            validade = self._converter_validade(validade_str, tipo)

            if not self.usuario_dao.buscar_por_cpf(cpf):
                return False, f"Usuário com CPF {cpf} não encontrado."

            atualizado = UsuarioFactory.criar_usuario(
                tipo=tipo, cpf=cpf, nome=nome, ativo=ativo, validade=validade
            )
            return self.usuario_dao.atualizar(atualizado)

        except CpfInvalidoError as e:
            return False, str(e)
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {e}"

    def remover_usuario(self, cpf):
        if not cpf:
            return False, "CPF não informado."
        try:
            return self.usuario_dao.remover(cpf)
        except Exception as e:
            return False, f"Erro inesperado: {e}"

    def listar_usuarios(self):
        try:
            return self.usuario_dao.listar_todos()
        except Exception as e:
            print(f"Erro ao listar usuários: {e}")
            return None

    def buscar_por_cpf(self, cpf):
        try:
            return self.usuario_dao.buscar_por_cpf(cpf)
        except Exception as e:
            print(f"Erro ao buscar usuário: {e}")
            return None

    def filtrar_usuarios(self, termo):
        try:
            return self.usuario_dao.buscar_por_termo(termo)
        except Exception as e:
            print(f"Erro ao filtrar usuários: {e}")
            return []
