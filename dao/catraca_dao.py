import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.catraca import Catraca
from dao.db_config import DatabaseConfig
from dao.generic_dao import GenericDAO


class CatracaDAO(GenericDAO):
    """
    DAO da entidade Catraca. O estado atual (padrão State) é persistido pelo
    seu nome ("Bloqueada"/"Liberada"/"Manutencao") e reconstruído na leitura.

    Tabela tb_catracas:
        cat_codigo       VARCHAR(10) PRIMARY KEY
        cat_localizacao  VARCHAR(120) NOT NULL
        cat_estado       VARCHAR(20)  NOT NULL
    """

    def __init__(self):
        self.conexao = DatabaseConfig.get_connection()

    def salvar(self, catraca: Catraca):
        if not self.conexao:
            raise Exception("Sem conexão com o BD")

        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = """INSERT INTO tb_catracas
                       (cat_codigo, cat_localizacao, cat_estado)
                       VALUES (%s, %s, %s)"""
            cursor.execute(query, (
                catraca.codigo,
                catraca.localizacao,
                catraca.nome_estado(),
            ))
            self.conexao.commit()
            return True, "Catraca cadastrada com sucesso"

        except Exception as e:
            print(f"Erro ao inserir catraca {catraca.codigo}: {e}")
            self.conexao.rollback()
            return False, f"Erro ao inserir catraca: {e}"

        finally:
            if cursor:
                cursor.close()

    def listar_todos(self):
        if not self.conexao:
            return []

        cursor = None
        try:
            cursor = self.conexao.cursor()
            cursor.execute("""SELECT cat_codigo, cat_localizacao, cat_estado
                              FROM tb_catracas ORDER BY cat_codigo""")
            return [self._linha_para_catraca(l) for l in cursor.fetchall()]

        except Exception as e:
            print(f"Erro ao listar catracas: {e}")
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
            cursor.execute("DELETE FROM tb_catracas WHERE cat_codigo = %s",
                           (id_objeto.strip().upper(),))
            self.conexao.commit()
            if cursor.rowcount == 0:
                return False, "Catraca não encontrada"
            return True, "Catraca removida com sucesso"

        except Exception as e:
            print(f"Erro ao remover catraca {id_objeto}: {e}")
            self.conexao.rollback()
            return False, (f"Não foi possível remover. Verifique se há acessos "
                           f"registrados para esta catraca. Detalhe: {e}")

        finally:
            if cursor:
                cursor.close()

    def atualizar(self, catraca: Catraca):
        if not self.conexao:
            return False, "Sem conexão com o BD"

        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = """UPDATE tb_catracas
                       SET cat_localizacao = %s, cat_estado = %s
                       WHERE cat_codigo = %s"""
            cursor.execute(query, (
                catraca.localizacao,
                catraca.nome_estado(),
                catraca.codigo,
            ))
            self.conexao.commit()
            if cursor.rowcount == 0:
                return False, "Catraca não encontrada para atualização"
            return True, "Catraca atualizada com sucesso"

        except Exception as e:
            print(f"Erro ao atualizar catraca {catraca.codigo}: {e}")
            self.conexao.rollback()
            return False, f"Erro ao atualizar catraca: {e}"

        finally:
            if cursor:
                cursor.close()

    # ------------------------------------------------------------------
    def buscar_por_codigo(self, codigo: str):
        if not self.conexao:
            return None

        cursor = None
        try:
            cursor = self.conexao.cursor()
            cursor.execute("""SELECT cat_codigo, cat_localizacao, cat_estado
                              FROM tb_catracas WHERE cat_codigo = %s""",
                           (codigo.strip().upper(),))
            linha = cursor.fetchone()
            return self._linha_para_catraca(linha) if linha else None

        except Exception as e:
            print(f"Erro ao buscar catraca {codigo}: {e}")
            return None

        finally:
            if cursor:
                cursor.close()

    def _linha_para_catraca(self, linha):
        codigo, localizacao, estado = linha
        return Catraca(codigo=codigo, localizacao=localizacao, estado_nome=estado)
