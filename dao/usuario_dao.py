import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.usuario import UsuarioFactory, Usuario
from dao.db_config import DatabaseConfig
from dao.generic_dao import GenericDAO


class UsuarioDAO(GenericDAO):
    """
    DAO da entidade Usuario. Usa herança de tabela única: a coluna
    ``usu_tipo`` indica a subclasse concreta (Aluno/Funcionario/Visitante),
    recriada pela ``UsuarioFactory`` ao ler do banco.

    Cada método abre e fecha sua própria conexão para evitar conexões
    presas em sessões longas (padrão dos demais DAOs do projeto).
    """

    _SELECT_BASE = """SELECT usu_cpf, usu_nome, usu_tipo, usu_ativo, usu_validade
                      FROM tb_usuarios"""

    def salvar(self, usuario: Usuario):
        conexao = DatabaseConfig.get_connection()
        if not conexao:
            return False, "Sem conexão com o BD"
        try:
            with conexao.cursor() as cur:
                cur.execute(
                    """INSERT INTO tb_usuarios
                       (usu_cpf, usu_nome, usu_tipo, usu_ativo, usu_validade)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (usuario.cpf, usuario.nome, usuario.tipo.value,
                     usuario.ativo, usuario.validade),
                )
                conexao.commit()
            return True, "Usuário cadastrado com sucesso"
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao inserir usuário {usuario.cpf}: {e}")
            return False, f"Erro ao inserir usuário: {e}"
        finally:
            conexao.close()

    def listar_todos(self):
        conexao = DatabaseConfig.get_connection()
        if not conexao:
            return []
        try:
            with conexao.cursor() as cur:
                cur.execute(self._SELECT_BASE + " ORDER BY usu_nome")
                return [self._linha_para_usuario(l) for l in cur.fetchall()]
        except Exception as e:
            print(f"Erro ao listar usuários: {e}")
            return []
        finally:
            conexao.close()

    def remover(self, id_objeto: str):
        conexao = DatabaseConfig.get_connection()
        if not conexao:
            return False, "Sem conexão com o BD"
        try:
            with conexao.cursor() as cur:
                cur.execute(
                    "DELETE FROM tb_usuarios WHERE usu_cpf = %s",
                    ("".join(filter(str.isdigit, id_objeto)),),
                )
                conexao.commit()
                if cur.rowcount == 0:
                    return False, "Usuário não encontrado"
            return True, "Usuário removido com sucesso"
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao remover usuário {id_objeto}: {e}")
            return False, (
                "Não foi possível remover. Verifique se há acessos "
                f"registrados para este usuário. Detalhe: {e}"
            )
        finally:
            conexao.close()

    def atualizar(self, usuario: Usuario):
        conexao = DatabaseConfig.get_connection()
        if not conexao:
            return False, "Sem conexão com o BD"
        try:
            with conexao.cursor() as cur:
                cur.execute(
                    """UPDATE tb_usuarios
                       SET usu_nome = %s, usu_tipo = %s,
                           usu_ativo = %s, usu_validade = %s
                       WHERE usu_cpf = %s""",
                    (usuario.nome, usuario.tipo.value, usuario.ativo,
                     usuario.validade, usuario.cpf),
                )
                conexao.commit()
                if cur.rowcount == 0:
                    return False, "Usuário não encontrado para atualização"
            return True, "Usuário atualizado com sucesso"
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao atualizar usuário {usuario.cpf}: {e}")
            return False, f"Erro ao atualizar usuário: {e}"
        finally:
            conexao.close()

    def buscar_por_cpf(self, cpf: str):
        conexao = DatabaseConfig.get_connection()
        if not conexao:
            return None
        try:
            with conexao.cursor() as cur:
                cur.execute(
                    self._SELECT_BASE + " WHERE usu_cpf = %s",
                    ("".join(filter(str.isdigit, cpf)),),
                )
                linha = cur.fetchone()
            return self._linha_para_usuario(linha) if linha else None
        except Exception as e:
            print(f"Erro ao buscar usuário {cpf}: {e}")
            return None
        finally:
            conexao.close()

    def buscar_por_termo(self, termo: str):
        """
        Busca/filtro por parte do nome OU do CPF (usado na tela de listagem).
        """
        conexao = DatabaseConfig.get_connection()
        if not conexao:
            return []
        try:
            termo = (termo or "").strip()
            if not termo:
                return self.listar_todos()

            termo_like = f"%{termo}%"
            digitos = "".join(filter(str.isdigit, termo))

            with conexao.cursor() as cur:
                if digitos:
                    cur.execute(
                        self._SELECT_BASE + """
                        WHERE usu_nome ILIKE %s OR usu_cpf LIKE %s
                        ORDER BY usu_nome""",
                        (termo_like, f"%{digitos}%"),
                    )
                else:
                    cur.execute(
                        self._SELECT_BASE + " WHERE usu_nome ILIKE %s ORDER BY usu_nome",
                        (termo_like,),
                    )
                return [self._linha_para_usuario(l) for l in cur.fetchall()]
        except Exception as e:
            print(f"Erro ao filtrar usuários: {e}")
            return []
        finally:
            conexao.close()

    # ------------------------------------------------------------------
    def _linha_para_usuario(self, linha):
        cpf, nome, tipo, ativo, validade = linha
        return UsuarioFactory.criar_usuario(
            tipo=tipo, cpf=cpf, nome=nome, ativo=ativo, validade=validade
        )
