"""DAO de Administrador — CRUD + autenticação por login/senha (hash)."""
from psycopg2 import Error

from dao.db_config import DatabaseConfig
from dao.generic_dao import GenericDAO
from model.administrador import Administrador, PerfilAdmin


class AdministradorDAO(GenericDAO):
    """Persiste e recupera administradores do sistema."""

    # ------------------------------------------------------------------
    def _linha_para_admin(self, row):
        if row is None:
            return None
        return Administrador(
            id_=row[0],
            login=row[1],
            nome=row[2],
            senha_hash=row[3],
            perfil=PerfilAdmin(row[4]),
            ativo=row[5],
        )

    # ------------------------------------------------------------------
    def salvar(self, administrador: Administrador):
        sql = (
            "INSERT INTO tb_administradores "
            "(adm_login, adm_nome, adm_senha, adm_perfil, adm_ativo) "
            "VALUES (%s, %s, %s, %s, %s) RETURNING adm_id"
        )
        conexao = DatabaseConfig.get_connection()
        if not conexao:
            return False, "Erro de conexão com o banco de dados."
        try:
            with conexao.cursor() as cur:
                cur.execute(sql, (
                    administrador.login,
                    administrador.nome,
                    administrador.senha_hash,
                    administrador.perfil.value,
                    administrador.ativo,
                ))
                administrador.id = cur.fetchone()[0]
                conexao.commit()
            return True, "Administrador cadastrado com sucesso."
        except Error as e:
            conexao.rollback()
            # Erro de chave única (login duplicado)
            if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
                return False, f"Já existe um administrador com o login '{administrador.login}'."
            print(f"Erro ao inserir administrador: {e}")
            return False, f"Erro ao cadastrar administrador: {e}"
        finally:
            conexao.close()

    def atualizar(self, administrador: Administrador):
        """
        Atualiza nome, perfil e ativo. A senha só é atualizada se
        administrador.senha_hash estiver preenchida (caso contrário, mantém).
        """
        conexao = DatabaseConfig.get_connection()
        if not conexao:
            return False, "Erro de conexão com o banco de dados."
        try:
            with conexao.cursor() as cur:
                if administrador.senha_hash:
                    cur.execute(
                        "UPDATE tb_administradores "
                        "SET adm_nome=%s, adm_perfil=%s, adm_ativo=%s, adm_senha=%s "
                        "WHERE adm_login=%s",
                        (administrador.nome, administrador.perfil.value,
                         administrador.ativo, administrador.senha_hash,
                         administrador.login),
                    )
                else:
                    cur.execute(
                        "UPDATE tb_administradores "
                        "SET adm_nome=%s, adm_perfil=%s, adm_ativo=%s "
                        "WHERE adm_login=%s",
                        (administrador.nome, administrador.perfil.value,
                         administrador.ativo, administrador.login),
                    )
                if cur.rowcount == 0:
                    return False, "Administrador não encontrado."
                conexao.commit()
            return True, "Administrador atualizado com sucesso."
        except Error as e:
            conexao.rollback()
            print(f"Erro ao atualizar administrador: {e}")
            return False, f"Erro ao atualizar administrador: {e}"
        finally:
            conexao.close()

    def remover(self, login: str):
        conexao = DatabaseConfig.get_connection()
        if not conexao:
            return False, "Erro de conexão com o banco de dados."
        try:
            with conexao.cursor() as cur:
                cur.execute("DELETE FROM tb_administradores WHERE adm_login=%s", (login,))
                if cur.rowcount == 0:
                    return False, "Administrador não encontrado."
                conexao.commit()
            return True, "Administrador removido com sucesso."
        except Error as e:
            conexao.rollback()
            print(f"Erro ao remover administrador: {e}")
            return False, f"Erro ao remover administrador: {e}"
        finally:
            conexao.close()

    def listar_todos(self):
        sql = (
            "SELECT adm_id, adm_login, adm_nome, adm_senha, adm_perfil, adm_ativo "
            "FROM tb_administradores ORDER BY adm_login"
        )
        conexao = DatabaseConfig.get_connection()
        if not conexao:
            return None
        try:
            with conexao.cursor() as cur:
                cur.execute(sql)
                return [self._linha_para_admin(r) for r in cur.fetchall()]
        except Error as e:
            print(f"Erro ao listar administradores: {e}")
            return None
        finally:
            conexao.close()

    def buscar_por_id(self, id_):
        return self.buscar_por_login_interna("adm_id=%s", (id_,))

    def buscar_por_login(self, login: str):
        return self.buscar_por_login_interna("adm_login=%s", (login,))

    def buscar_por_login_interna(self, where: str, params: tuple):
        sql = (
            "SELECT adm_id, adm_login, adm_nome, adm_senha, adm_perfil, adm_ativo "
            f"FROM tb_administradores WHERE {where}"
        )
        conexao = DatabaseConfig.get_connection()
        if not conexao:
            return None
        try:
            with conexao.cursor() as cur:
                cur.execute(sql, params)
                return self._linha_para_admin(cur.fetchone())
        except Error as e:
            print(f"Erro ao buscar administrador: {e}")
            return None
        finally:
            conexao.close()

    # ------------------------------------------------------------------
    def autenticar(self, login: str, senha_texto: str):
        """
        Retorna o Administrador autenticado, ou None se as credenciais
        forem inválidas ou a conta estiver inativa.
        """
        adm = self.buscar_por_login(login)
        if adm is None:
            return None
        if not adm.ativo:
            return None
        if not adm.verificar_senha(senha_texto):
            return None
        return adm
