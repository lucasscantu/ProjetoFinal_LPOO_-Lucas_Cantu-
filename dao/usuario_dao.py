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

    Tabela tb_usuarios:
        usu_cpf       VARCHAR(11) PRIMARY KEY
        usu_nome      VARCHAR(120) NOT NULL
        usu_tipo      VARCHAR(20)  NOT NULL
        usu_ativo     BOOLEAN      NOT NULL
        usu_validade  DATE         NULL
    """

    def __init__(self):
        self.conexao = DatabaseConfig.get_connection()

    def salvar(self, usuario: Usuario):
        if not self.conexao:
            raise Exception("Sem conexão com o BD")

        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = """INSERT INTO tb_usuarios
                       (usu_cpf, usu_nome, usu_tipo, usu_ativo, usu_validade)
                       VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, (
                usuario.cpf,
                usuario.nome,
                usuario.tipo.value,
                usuario.ativo,
                usuario.validade,
            ))
            self.conexao.commit()
            return True, "Usuário cadastrado com sucesso"

        except Exception as e:
            print(f"Erro ao inserir usuário {usuario.cpf}: {e}")
            self.conexao.rollback()
            return False, f"Erro ao inserir usuário: {e}"

        finally:
            if cursor:
                cursor.close()

    def listar_todos(self):
        if not self.conexao:
            return []

        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = """SELECT usu_cpf, usu_nome, usu_tipo, usu_ativo, usu_validade
                       FROM tb_usuarios ORDER BY usu_nome"""
            cursor.execute(query)
            return [self._linha_para_usuario(l) for l in cursor.fetchall()]

        except Exception as e:
            print(f"Erro ao listar usuários: {e}")
            return []

        finally:
            if cursor:
                cursor.close()

    def remover(self, id_objeto: str):
        if not self.conexao:
            return False, "Sem conexão com o BD"

        cursor = None
        try:
            cursor = self.conexao.cursor()
            cursor.execute("DELETE FROM tb_usuarios WHERE usu_cpf = %s",
                           ("".join(filter(str.isdigit, id_objeto)),))
            self.conexao.commit()
            if cursor.rowcount == 0:
                return False, "Usuário não encontrado"
            return True, "Usuário removido com sucesso"

        except Exception as e:
            print(f"Erro ao remover usuário {id_objeto}: {e}")
            self.conexao.rollback()
            # Erro comum: FK em tb_acessos impedindo a exclusão
            return False, (f"Não foi possível remover. Verifique se há acessos "
                           f"registrados para este usuário. Detalhe: {e}")

        finally:
            if cursor:
                cursor.close()

    def atualizar(self, usuario: Usuario):
        if not self.conexao:
            return False, "Sem conexão com o BD"

        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = """UPDATE tb_usuarios
                       SET usu_nome = %s, usu_tipo = %s,
                           usu_ativo = %s, usu_validade = %s
                       WHERE usu_cpf = %s"""
            cursor.execute(query, (
                usuario.nome,
                usuario.tipo.value,
                usuario.ativo,
                usuario.validade,
                usuario.cpf,
            ))
            self.conexao.commit()
            if cursor.rowcount == 0:
                return False, "Usuário não encontrado para atualização"
            return True, "Usuário atualizado com sucesso"

        except Exception as e:
            print(f"Erro ao atualizar usuário {usuario.cpf}: {e}")
            self.conexao.rollback()
            return False, f"Erro ao atualizar usuário: {e}"

        finally:
            if cursor:
                cursor.close()

    # ------------------------------------------------------------------
    # Consultas auxiliares
    # ------------------------------------------------------------------
    def buscar_por_cpf(self, cpf: str):
        if not self.conexao:
            return None

        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = """SELECT usu_cpf, usu_nome, usu_tipo, usu_ativo, usu_validade
                       FROM tb_usuarios WHERE usu_cpf = %s"""
            cursor.execute(query, ("".join(filter(str.isdigit, cpf)),))
            linha = cursor.fetchone()
            return self._linha_para_usuario(linha) if linha else None

        except Exception as e:
            print(f"Erro ao buscar usuário {cpf}: {e}")
            return None

        finally:
            if cursor:
                cursor.close()

    def buscar_por_termo(self, termo: str):
        """
        Busca/filtro por parte do nome OU do CPF (usado na tela de listagem).
        """
        if not self.conexao:
            return []

        cursor = None
        try:
            cursor = self.conexao.cursor()
            termo = (termo or "").strip()

            # Sem termo: devolve todos (equivale a "limpar o filtro").
            if not termo:
                return self.listar_todos()

            termo_like = f"%{termo}%"
            digitos = "".join(filter(str.isdigit, termo))

            # A condição por CPF só é aplicada quando o termo contém dígitos,
            # evitando que um '%%' acabe casando com todos os registros.
            if digitos:
                query = """SELECT usu_cpf, usu_nome, usu_tipo, usu_ativo, usu_validade
                           FROM tb_usuarios
                           WHERE usu_nome ILIKE %s OR usu_cpf LIKE %s
                           ORDER BY usu_nome"""
                cursor.execute(query, (termo_like, f"%{digitos}%"))
            else:
                query = """SELECT usu_cpf, usu_nome, usu_tipo, usu_ativo, usu_validade
                           FROM tb_usuarios
                           WHERE usu_nome ILIKE %s
                           ORDER BY usu_nome"""
                cursor.execute(query, (termo_like,))

            return [self._linha_para_usuario(l) for l in cursor.fetchall()]

        except Exception as e:
            print(f"Erro ao filtrar usuários: {e}")
            return []

        finally:
            if cursor:
                cursor.close()

    # ------------------------------------------------------------------
    # Conversão linha -> objeto
    # ------------------------------------------------------------------
    def _linha_para_usuario(self, linha):
        cpf, nome, tipo, ativo, validade = linha
        return UsuarioFactory.criar_usuario(
            tipo=tipo, cpf=cpf, nome=nome, ativo=ativo, validade=validade
        )
