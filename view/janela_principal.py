"""
Janela Principal (tk.Tk) — concentra a barra de menus.
A composição dos menus é GATEADA pelo perfil do administrador logado:

    ADMIN     -> Cadastros, Operação, Administração, Ajuda
    OPERADOR  -> Operação, Ajuda

Mostra também uma barra de status com o usuário corrente e seu perfil.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox

from model.sessao import sessao_atual
from model.administrador import PerfilAdmin
from view.estilos import aplicar_tema, COR


class JanelaPrincipal(tk.Tk):
    """Janela raiz com menus e área central informativa."""

    def __init__(self):
        super().__init__()
        self.title("Sistema de Catraca Eletrônica — LPOO 2026/1")
        self.geometry("700x500")
        self.configure(bg=COR["fundo"])

        aplicar_tema(self)

        self._criar_menu()
        self._criar_conteudo()
        self._criar_status_bar()

    # ------------------------------------------------------------------
    def _eh_admin(self) -> bool:
        return sessao_atual.pode(PerfilAdmin.ADMIN)

    # ------------------------------------------------------------------
    def _criar_menu(self):
        barra = tk.Menu(self)

        # --- Cadastros: somente ADMIN ---
        if self._eh_admin():
            menu_cad = tk.Menu(barra, tearoff=0)
            menu_cad.add_command(label="Usuários", command=self._abrir_usuarios)
            menu_cad.add_command(label="Catracas", command=self._abrir_catracas)
            barra.add_cascade(label="Cadastros", menu=menu_cad)

        # --- Operação: todos autenticados (ADMIN + OPERADOR) ---
        menu_op = tk.Menu(barra, tearoff=0)
        menu_op.add_command(label="Simular Acesso", command=self._abrir_simular)
        menu_op.add_command(label="Histórico de Acessos", command=self._abrir_acessos)
        barra.add_cascade(label="Operação", menu=menu_op)

        # --- Administração: somente ADMIN ---
        if self._eh_admin():
            menu_adm = tk.Menu(barra, tearoff=0)
            menu_adm.add_command(label="Administradores", command=self._abrir_admins)
            barra.add_cascade(label="Administração", menu=menu_adm)

        # --- Ajuda ---
        menu_ajuda = tk.Menu(barra, tearoff=0)
        menu_ajuda.add_command(label="Sobre", command=self._abrir_sobre)
        barra.add_cascade(label="Ajuda", menu=menu_ajuda)

        # --- Conta ---
        menu_conta = tk.Menu(barra, tearoff=0)
        menu_conta.add_command(label="Sair (Logout)", command=self._logout)
        menu_conta.add_separator()
        menu_conta.add_command(label="Encerrar Aplicação", command=self._sair)
        barra.add_cascade(label="Conta", menu=menu_conta)

        self.config(menu=barra)

    # ------------------------------------------------------------------
    def _criar_conteudo(self):
        # Cabeçalho colorido
        cab = tk.Frame(self, bg=COR["primaria"])
        cab.pack(fill="x")
        ttk.Label(cab, text="🛂  Sistema de Catraca Eletrônica",
                  style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(cab, text="Controle de Acesso — Disciplina LPOO 2026/1",
                  style="Subtitulo.TLabel").pack(anchor="w")

        # Card central com o painel de operações
        wrapper = ttk.Frame(self, style="TFrame", padding=(24, 18))
        wrapper.pack(expand=True, fill="both")

        card = ttk.Frame(wrapper, style="Card.TFrame", padding=20)
        card.pack(expand=True, fill="both")

        ttk.Label(card, text="Painel de Operações", style="Card.TLabel",
                  font=("Helvetica", 14, "bold")).pack(anchor="w", pady=(0, 10))

        # Botões de atalho para as ações principais
        grid = ttk.Frame(card, style="Card.TFrame")
        grid.pack(fill="both", expand=True)
        grid.columnconfigure((0, 1), weight=1)

        if self._eh_admin():
            self._botao_card(grid, "👤 Gerenciar Usuários",
                             "Cadastrar e manter alunos, funcionários e visitantes",
                             self._abrir_usuarios, row=0, col=0,
                             style="Primary.TButton")
            self._botao_card(grid, "🚪 Gerenciar Catracas",
                             "Cadastros, edição e envio para manutenção",
                             self._abrir_catracas, row=0, col=1,
                             style="Primary.TButton")

        self._botao_card(grid, "▶ Simular Acesso",
                         "Validar e registrar uma passagem na catraca",
                         self._abrir_simular,
                         row=1 if self._eh_admin() else 0, col=0,
                         style="Success.TButton")
        self._botao_card(grid, "📜 Histórico de Acessos",
                         "Consultar e filtrar registros de passagens",
                         self._abrir_acessos,
                         row=1 if self._eh_admin() else 0, col=1)

        if self._eh_admin():
            self._botao_card(grid, "⚙ Administradores",
                             "Operadores do sistema (acesso restrito a ADMIN)",
                             self._abrir_admins, row=2, col=0)
        self._botao_card(grid, "ℹ Sobre",
                         "Informações do sistema e do autor",
                         self._abrir_sobre,
                         row=(2 if self._eh_admin() else 1),
                         col=(1 if self._eh_admin() else 0))

    def _botao_card(self, parent, titulo, descricao, comando, row, col, style="TButton"):
        bloco = ttk.Frame(parent, style="Card.TFrame")
        bloco.grid(row=row, column=col, sticky="nsew", padx=8, pady=6)
        ttk.Button(bloco, text=titulo, style=style, command=comando).pack(
            fill="x", padx=4, pady=(4, 2)
        )
        ttk.Label(bloco, text=descricao, style="Card.TLabel",
                  foreground=COR["mudo"], font=("Helvetica", 9)).pack(
            anchor="w", padx=6
        )

    # ------------------------------------------------------------------
    def _criar_status_bar(self):
        adm = sessao_atual.administrador
        if adm:
            texto = (f"Logado como:  {adm.nome}   "
                     f"|   Login: {adm.login}   "
                     f"|   Perfil: {adm.perfil.descricao}")
        else:
            texto = "Não autenticado"
        ttk.Label(self, text=texto, style="Status.TLabel",
                  anchor="w").pack(side="bottom", fill="x")

    # ==================================================================
    # AÇÕES DOS MENUS
    # ==================================================================
    def _abrir_usuarios(self):
        if not self._eh_admin():
            self._sem_permissao(); return
        self._abrir("view.usuario_list_view", "JanelaListagemUsuarios", "Usuários")

    def _abrir_catracas(self):
        if not self._eh_admin():
            self._sem_permissao(); return
        self._abrir("view.catraca_list_view", "JanelaListagemCatracas", "Catracas")

    def _abrir_admins(self):
        if not self._eh_admin():
            self._sem_permissao(); return
        self._abrir("view.admin_list_view", "JanelaListagemAdmins", "Administradores")

    def _abrir_simular(self):
        self._abrir("view.simular_acesso_view", "JanelaSimularAcesso", "Simular Acesso")

    def _abrir_acessos(self):
        self._abrir("view.acesso_list_view", "JanelaListagemAcessos", "Histórico de Acessos")

    def _abrir_sobre(self):
        self._abrir("view.sobre_view", "JanelaSobre", "Sobre")

    def _abrir(self, modulo, classe, rotulo):
        try:
            mod = __import__(modulo, fromlist=[classe])
            janela = getattr(mod, classe)(self)
            janela.transient(self)
        except Exception as e:
            messagebox.showerror("Erro",
                                 f"Não foi possível abrir a tela '{rotulo}':\n{e}",
                                 parent=self)

    def _sem_permissao(self):
        messagebox.showwarning(
            "Acesso restrito",
            "Esta operação é restrita ao perfil ADMIN.",
            parent=self,
        )

    # ------------------------------------------------------------------
    def _logout(self):
        if messagebox.askyesno("Logout", "Encerrar a sessão atual e voltar ao login?",
                                parent=self):
            sessao_atual.logout()
            self.destroy()  # main.py reabrirá a janela de login

    def _sair(self):
        if messagebox.askyesno("Encerrar", "Deseja realmente encerrar a aplicação?",
                                parent=self):
            sessao_atual.logout()
            # encerra todo o processo sem reabrir o login
            os._exit(0)
