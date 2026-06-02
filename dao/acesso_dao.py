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

    Cada método abre e fecha sua própria conexão (sem estado compartilhado).
    """

    _SELECT_BASE = """
        SELECT a.ace_id, a.ace_data_hora, a.ace_tipo, a.ace_autorizado, a.ace_motivo,
               u.usu_cpf, u.usu_nome, u.usu_tipo, u.usu_ativo, u.usu_validade,
               c.cat_codigo, c.cat_localizacao, c.cat_estado
        FROM tb_acessos a
        INNER JOIN tb_usuarios u ON u.usu_cpf = a.usu_cpf
        INNER JOIN tb_catracas c ON c.cat_codigo = a.cat_codigo
    """

    def salvar(self, acesso: Acesso):
        conexao = DatabaseConfig.get_connection()
        if not conexao:
            raise Exception("Sem conexão com o BD")
        try:
            with conexao.cursor() as cur:
                cur.execute(
                    """INSERT INTO tb_acessos
                       (usu_cpf, cat_codigo, ace_data_hora, ace_tipo,
                        ace_autorizado, ace_motivo)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       RETURNING ace_id""",
                    (acesso.usuario.cpf, acesso.catraca.codigo,
                     acesso.data_hora, acesso.tipo.value,
                     acesso.autorizado, acesso.motivo),
                )
                acesso.id = cur.fetchone()[0]
                conexao.commit()
            return True, f"Acesso registrado (ID {acesso.id})"
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao registrar acesso: {e}")
            return False, f"Erro ao registrar acesso: {e}"
        finally:
            conexao.close()

    def listar_todos(self):
        conexao = DatabaseConfig.get_connection()
        if not conexao:
            return []
        try:
            with conexao.cursor() as cur:
                cur.execute(self._SELECT_BASE + " ORDER BY a.ace_data_hora DESC")
                return [self._linha_para_acesso(l) for l in cur.fetchall()]
        except Exception as e:
            print(f"Erro ao listar acessos: {e}")
            return []
        finally:
            conexao.close()

    def remover(self, id_objeto):
        conexao = DatabaseConfig.get_connection()
        if not conexao:
            return False, "Sem conexão com o BD"
        try:
            with conexao.cursor() as cur:
                cur.execute("DELETE FROM tb_acessos WHERE ace_id = %s", (id_objeto,))
                conexao.commit()
                if cur.rowcount == 0:
                    return False, "Acesso não encontrado"
            return True, "Registro de acesso removido com sucesso"
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao remover acesso {id_objeto}: {e}")
            return False, f"Erro ao remover acesso: {e}"
        finally:
            conexao.close()

    def atualizar(self, acesso: Acesso):
        """Acessos geralmente são imutáveis; método implementado para satisfazer o contrato DAO."""
        if acesso.id is None:
            return False, "ID do acesso é obrigatório para atualização."
        conexao = DatabaseConfig.get_connection()
        if not conexao:
            return False, "Sem conexão com o BD"
        try:
            with conexao.cursor() as cur:
                cur.execute(
                    """UPDATE tb_acessos
                       SET usu_cpf = %s, cat_codigo = %s, ace_data_hora = %s,
                           ace_tipo = %s, ace_autorizado = %s, ace_motivo = %s
                       WHERE ace_id = %s""",
                    (acesso.usuario.cpf, acesso.catraca.codigo, acesso.data_hora,
                     acesso.tipo.value, acesso.autorizado, acesso.motivo, acesso.id),
                )
                conexao.commit()
            return True, "Acesso atualizado com sucesso"
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao atualizar acesso {acesso.id}: {e}")
            return False, f"Erro ao atualizar acesso: {e}"
        finally:
            conexao.close()

    def listar_filtrado(self, resultado: str = "TODOS", cpf: str = ""):
        """
        Filtra os acessos por resultado (AUTORIZADO/NEGADO/TODOS) e/ou por CPF.
        """
        conexao = DatabaseConfig.get_connection()
        if not conexao:
            return []
        try:
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

            with conexao.cursor() as cur:
                cur.execute(query, params)
                return [self._linha_para_acesso(l) for l in cur.fetchall()]
        except Exception as e:
            print(f"Erro ao filtrar acessos: {e}")
            return []
        finally:
            conexao.close()

    def _linha_para_acesso(self, linha):
        (ace_id, data_hora, tipo, autorizado, motivo,
         usu_cpf, usu_nome, usu_tipo, usu_ativo, usu_validade,
         cat_codigo, cat_local, cat_estado) = linha

        usuario = UsuarioFactory.criar_usuario(
            tipo=usu_tipo, cpf=usu_cpf, nome=usu_nome,
            ativo=usu_ativo, validade=usu_validade
        )
        catraca = Catraca(
            codigo=cat_codigo, localizacao=cat_local, estado_nome=cat_estado
        )
        return Acesso(
            usuario=usuario, catraca=catraca,
            tipo=TipoAcesso(tipo), autorizado=autorizado,
            motivo=motivo or "", data_hora=data_hora, id_acesso=ace_id,
        )
