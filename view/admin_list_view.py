"""
Listagem de Administradores — acessível apenas a usuários com perfil ADMIN.
CRUD completo sobre operadores do sistema.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox

from control.administrador_controller import AdministradorController
from model.sessao import sessao_atual
from view.estilos import COR, criar_cabecalho, aplicar_zebra


class JanelaListagemAdmins(tk.Toplevel):
    """Listagem e CRUD de administradores/operadores do sistema."""

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Administradores")
        self.geometry("760x440")
        self.configure(bg=COR["fundo"])
        self.controller = AdministradorController()

        criar_cabecalho(
            self,
            "Administradores do Sistema",
            "Acesso restrito ao perfil ADMIN",
        )
        self._criar_widgets()
        self.carregar_dados()

        self.lift()
        self.focus_force()

    # ------------------------------------------------------------------
    def _criar_widgets(self):
        corpo = ttk.Frame(self, style="TFrame", padding=(20, 14))
        corpo.pack(expand=True, fill="both")

        frame_tree = ttk.Frame(corpo, style="TFrame")
        frame_tree.pack(expand=True, fill="both")

        scrollbar = ttk.Scrollbar(frame_tree)
        scrollbar.pack(side="right", fill="y")

        colunas = ("Login", "Nome", "Perfil", "Ativo")
        self.tree = ttk.Treeview(frame_tree, columns=colunas, show="headings",
                                 yscrollcommand=scrollbar.set)
        larguras = {"Login": 140, "Nome": 320, "Perfil": 130, "Ativo": 80}
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=larguras[col])
        self.tree.pack(expand=True, fill="both")
        scrollbar.config(command=self.tree.yview)

        botoes = ttk.Frame(corpo, style="TFrame")
        botoes.pack(fill="x", pady=(12, 0))
        ttk.Button(botoes, text="Novo", style="Primary.TButton",
                   command=self.abrir_novo).pack(side="left", padx=(0, 6))
        ttk.Button(botoes, text="Editar",
                   command=self.abrir_editar).pack(side="left", padx=6)
        ttk.Button(botoes, text="Remover", style="Danger.TButton",
                   command=self.remover).pack(side="left", padx=6)
        ttk.Button(botoes, text="Fechar",
                   command=self.destroy).pack(side="right")

    # ------------------------------------------------------------------
    def carregar_dados(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        admins = self.controller.listar_administradores()
        if admins is None:
            messagebox.showerror(
                "Permissão negada",
                "Apenas administradores podem acessar esta tela.",
                parent=self,
            )
            self.destroy()
            return
        for a in admins:
            self.tree.insert("", "end", values=(
                a.login, a.nome, a.perfil.descricao,
                "Sim" if a.ativo else "Não",
            ))
        aplicar_zebra(self.tree)

    def _login_selecionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um administrador.", parent=self)
            return None
        return self.tree.item(sel[0])["values"][0]

    # ------------------------------------------------------------------
    def abrir_novo(self):
        from view.admin_view import JanelaCadastroAdmin
        janela = JanelaCadastroAdmin(self)
        self.wait_window(janela)
        self.carregar_dados()

    def abrir_editar(self):
        login = self._login_selecionado()
        if not login:
            return
        adm = self.controller.buscar_por_login(str(login))
        if not adm:
            messagebox.showerror("Erro", "Administrador não encontrado.", parent=self)
            return
        from view.admin_view import JanelaCadastroAdmin
        janela = JanelaCadastroAdmin(self, admin_existente=adm)
        self.wait_window(janela)
        self.carregar_dados()

    def remover(self):
        login = self._login_selecionado()
        if not login:
            return
        if sessao_atual.autenticado and sessao_atual.administrador.login == str(login):
            messagebox.showwarning(
                "Não permitido",
                "Você não pode remover a si mesmo enquanto está logado.",
                parent=self,
            )
            return
        if messagebox.askyesno("Confirmar", f"Remover o administrador '{login}'?",
                                parent=self):
            sucesso, msg = self.controller.remover_administrador(str(login))
            if sucesso:
                messagebox.showinfo("Sucesso", msg, parent=self)
                self.carregar_dados()
            else:
                messagebox.showerror("Erro", msg, parent=self)
