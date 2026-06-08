"""
Controller de Administradores — autenticação (login) e CRUD.
As operações de CRUD exigem perfil ADMIN (verificado via Sessao).
"""
from dao.administrador_dao import AdministradorDAO
from model.administrador import Administrador, PerfilAdmin
from model.sessao import sessao_atual


class AdministradorController:
    """Concentra as regras de autenticação e administração de operadores."""

    def __init__(self):
        self.dao = AdministradorDAO()

    # ============================== AUTENTICAÇÃO ======================
    def autenticar(self, login: str, senha: str):
        """
        Tenta autenticar e abrir a sessão. Retorna (sucesso, mensagem,
        administrador) — em caso de falha o terceiro elemento é None.
        """
        login = (login or "").strip()
        senha = senha or ""
        if not login or not senha:
            return False, "Informe login e senha.", None

        adm = self.dao.autenticar(login, senha)
        if adm is None:
            return False, "Login ou senha inválidos (ou conta inativa).", None

        sessao_atual.login(adm)
        return True, f"Bem-vindo(a), {adm.nome}!", adm

    def logout(self):
        sessao_atual.logout()

    # ============================== CRUD (ADMIN) ======================
    def _exigir_admin(self):
        try:
            sessao_atual.exigir_admin()
            return True, None
        except PermissionError as e:
            return False, str(e)

    # ------------------------------------------------------------------
    def listar_administradores(self):
        if not sessao_atual.pode(PerfilAdmin.ADMIN):
            return None
        return self.dao.listar_todos()

    def buscar_por_login(self, login: str):
        if not sessao_atual.pode(PerfilAdmin.ADMIN):
            return None
        return self.dao.buscar_por_login(login)

    # ------------------------------------------------------------------
    def salvar_administrador(self, login, nome, senha, perfil, ativo=True):
        ok, msg = self._exigir_admin()
        if not ok:
            return False, msg

        login = (login or "").strip()
        nome = (nome or "").strip()
        if not login or not nome:
            return False, "Login e nome são obrigatórios."
        if not senha or len(senha) < 4:
            return False, "Senha obrigatória (mínimo 4 caracteres)."

        try:
            perfil_enum = perfil if isinstance(perfil, PerfilAdmin) \
                          else PerfilAdmin(str(perfil).upper())
        except ValueError:
            return False, "Perfil inválido (use ADMIN ou OPERADOR)."

        adm = Administrador(
            login=login, nome=nome, perfil=perfil_enum, ativo=bool(ativo),
            senha_hash=Administrador.hash_senha(senha),
        )
        return self.dao.salvar(adm)

    def atualizar_administrador(self, login, nome, perfil, ativo, nova_senha=""):
        ok, msg = self._exigir_admin()
        if not ok:
            return False, msg

        nome = (nome or "").strip()
        if not nome:
            return False, "Nome é obrigatório."

        try:
            perfil_enum = perfil if isinstance(perfil, PerfilAdmin) \
                          else PerfilAdmin(str(perfil).upper())
        except ValueError:
            return False, "Perfil inválido (use ADMIN ou OPERADOR)."

        existente = self.dao.buscar_por_login(login)
        if existente is None:
            return False, "Administrador não encontrado."

        # Trava de segurança: não permite rebaixar/desativar o próprio
        # usuário logado (evitando que o admin se tranque para fora).
        if sessao_atual.autenticado and sessao_atual.administrador.login == login:
            if perfil_enum != PerfilAdmin.ADMIN:
                return False, "Você não pode rebaixar seu próprio perfil enquanto está logado."
            if not ativo:
                return False, "Você não pode desativar a si mesmo."

        existente.nome = nome
        existente.perfil = perfil_enum
        existente.ativo = bool(ativo)
        existente.senha_hash = (
            Administrador.hash_senha(nova_senha) if nova_senha else None  # None = mantém
        )
        return self.dao.atualizar(existente)

    def remover_administrador(self, login: str):
        ok, msg = self._exigir_admin()
        if not ok:
            return False, msg

        if sessao_atual.autenticado and sessao_atual.administrador.login == login:
            return False, "Você não pode remover sua própria conta enquanto está logado."

        return self.dao.remover(login)
