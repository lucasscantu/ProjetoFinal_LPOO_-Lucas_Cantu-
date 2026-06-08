import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.usuario import UsuarioFactory
from model.catraca import Catraca
from model.acesso import Acesso, TipoAcesso
from dao.db_config import DatabaseConfig
from dao.generic_dao import GenericDAO


class AcessoDAO(GenericDAO):
    """
    DAO da entidade associativa Acesso. Faz JOIN com tb_usuarios e tb_catracas
    para reconstruir os objetos relacionados.

    Tabela tb_acessos:
        ace_id          SERIAL PRIMARY KEY
        usu_cpf         VARCHAR(11) FK -> tb_usuarios
        cat_codigo      VARCHAR(10) FK -> tb_catracas
        ace_data_hora   TIMESTAMP NOT NULL
        ace_tipo        VARCHAR(10) NOT NULL  (ENTRADA / SAIDA)
        ace_autorizado  BOOLEAN NOT NULL
        ace_motivo      VARCHAR(200)
    """

    _SELECT_BASE = """
        SELECT a.ace_id, a.ace_data_hora, a.ace_tipo, a.ace_autorizado, a.ace_motivo,
               u.usu_cpf, u.usu_nome, u.usu_tipo, u.usu_ativo, u.usu_validade,
               c.cat_codigo, c.cat_localizacao, c.cat_estado
        FROM tb_acessos a
        INNER JOIN tb_usuarios u ON u.usu_cpf = a.usu_cpf
        INNER JOIN tb_catracas c ON c.cat_codigo = a.cat_codigo
    """

    def __init__(self):
        self.conexao = DatabaseConfig.get_connection()

    def salvar(self, acesso: Acesso):
        if not self.conexao:
            raise Exception("Sem conexão com o BD")

        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = """INSERT INTO tb_acessos
                       (usu_cpf, cat_codigo, ace_data_hora, ace_tipo,
                        ace_autorizado, ace_motivo)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       RETURNING ace_id"""
            cursor.execute(query, (
                acesso.usuario.cpf,
                acesso.catraca.codigo,
                acesso.data_hora,
                acesso.tipo.value,
                acesso.autorizado,
                acesso.motivo,
            ))
            acesso.id = cursor.fetchone()[0]
            self.conexao.commit()
            return True, f"Acesso registrado (ID {acesso.id})"

        except Exception as e:
            print(f"Erro ao registrar acesso: {e}")
            self.conexao.rollback()
            return False, f"Erro ao registrar acesso: {e}"

        finally:
            if cursor:
                cursor.close()

    def listar_todos(self):
        if not self.conexao:
            return []

        cursor = None
        try:
            cursor = self.conexao.cursor()
            cursor.execute(self._SELECT_BASE + " ORDER BY a.ace_data_hora DESC")
            return [self._linha_para_acesso(l) for l in cursor.fetchall()]

        except Exception as e:
            print(f"Erro ao listar acessos: {e}")
            return []

        finally:
            if cursor:
                cursor.close()

    def remover(self, id_objeto):
        if not self.conexao:
            return False, "Sem conexão com o BD"

        cursor = None
        try:
            cursor = self.conexao.cursor()
            cursor.execute("DELETE FROM tb_acessos WHERE ace_id = %s", (id_objeto,))
            self.conexao.commit()
            if cursor.rowcount == 0:
                return False, "Acesso não encontrado"
            return True, "Registro de acesso removido com sucesso"

        except Exception as e:
            print(f"Erro ao remover acesso {id_objeto}: {e}")
            self.conexao.rollback()
            return False, f"Erro ao remover acesso: {e}"

        finally:
            if cursor:
                cursor.close()

    def atualizar(self, acesso: Acesso):
        if not self.conexao:
            return False, "Sem conexão com o BD"
        if acesso.id is None:
            return False, "ID do acesso é obrigatório para atualização."

        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = """UPDATE tb_acessos
                       SET usu_cpf = %s, cat_codigo = %s, ace_data_hora = %s,
                           ace_tipo = %s, ace_autorizado = %s, ace_motivo = %s
                       WHERE ace_id = %s"""
            cursor.execute(query, (
                acesso.usuario.cpf,
                acesso.catraca.codigo,
                acesso.data_hora,
                acesso.tipo.value,
                acesso.autorizado,
                acesso.motivo,
                acesso.id,
            ))
            self.conexao.commit()
            return True, "Acesso atualizado com sucesso"

        except Exception as e:
            print(f"Erro ao atualizar acesso {acesso.id}: {e}")
            self.conexao.rollback()
            return False, f"Erro ao atualizar acesso: {e}"

        finally:
            if cursor:
                cursor.close()

    # ------------------------------------------------------------------
    def listar_filtrado(self, resultado: str = "TODOS", cpf: str = ""):
        """
        Filtra os acessos por resultado (AUTORIZADO/NEGADO/TODOS) e/ou por CPF.
        Usado na tela de listagem de acessos (requisito de filtro/busca).
        """
        if not self.conexao:
            return []

        cursor = None
        try:
            cursor = self.conexao.cursor()
            condicoes = []
            params = []

            if resultado == "AUTORIZADO":
                condicoes.append("a.ace_autorizado = TRUE")
            elif resultado == "NEGADO":
                condicoes.append("a.ace_autorizado = FALSE")

            cpf_dig = "".join(filter(str.isdigit, cpf or ""))
            if cpf_dig:
                condicoes.append("a.usu_cpf LIKE %s")
                params.append(f"%{cpf_dig}%")

            query = self._SELECT_BASE
            if condicoes:
                query += " WHERE " + " AND ".join(condicoes)
            query += " ORDER BY a.ace_data_hora DESC"

            cursor.execute(query, params)
            return [self._linha_para_acesso(l) for l in cursor.fetchall()]

        except Exception as e:
            print(f"Erro ao filtrar acessos: {e}")
            return []

        finally:
            if cursor:
                cursor.close()

    # ------------------------------------------------------------------
    def _linha_para_acesso(self, linha):
        (ace_id, data_hora, tipo, autorizado, motivo,
         usu_cpf, usu_nome, usu_tipo, usu_ativo, usu_validade,
         cat_codigo, cat_local, cat_estado) = linha

        usuario = UsuarioFactory.criar_usuario(
            tipo=usu_tipo, cpf=usu_cpf, nome=usu_nome,
            ativo=usu_ativo, validade=usu_validade
        )
        catraca = Catraca(codigo=cat_codigo, localizacao=cat_local, estado_nome=cat_estado)

        return Acesso(
            usuario=usuario,
            catraca=catraca,
            tipo=TipoAcesso(tipo),
            autorizado=autorizado,
            motivo=motivo or "",
            data_hora=data_hora,
            id_acesso=ace_id,
        )
