"""Cadastro/edição de Administrador. Em edição, login fica bloqueado."""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox

from control.administrador_controller import AdministradorController
from model.administrador import PerfilAdmin
from view.estilos import COR, criar_cabecalho


class JanelaCadastroAdmin(tk.Toplevel):
    """Formulário de cadastro/edição de administrador."""

    PERFIS = [PerfilAdmin.ADMIN.value, PerfilAdmin.OPERADOR.value]

    def __init__(self, master=None, admin_existente=None):
        super().__init__(master)
        self.admin_existente = admin_existente
        self.controller = AdministradorController()

        modo = "Atualizar" if admin_existente else "Cadastrar"
        self.title(f"{modo} Administrador")
        self.geometry("440x450")
        self.resizable(False, False)
        self.configure(bg=COR["fundo"])

        criar_cabecalho(self, f"{modo} Administrador")

        corpo = ttk.Frame(self, style="TFrame", padding=(24, 16))
        corpo.pack(expand=True, fill="both")

        card = ttk.Frame(corpo, style="Card.TFrame", padding=18)
        card.pack(fill="both", expand=True)
        card.columnconfigure(1, weight=1)

        ttk.Label(card, text="Login:", style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=6)
        self.txt_login = ttk.Entry(card)
        self.txt_login.grid(row=0, column=1, sticky="ew", pady=6, padx=(10, 0))

        ttk.Label(card, text="Nome:", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=6)
        self.txt_nome = ttk.Entry(card)
        self.txt_nome.grid(row=1, column=1, sticky="ew", pady=6, padx=(10, 0))

        rotulo_senha = "Nova senha (opcional):" if admin_existente else "Senha:"
        ttk.Label(card, text=rotulo_senha, style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=6)
        self.txt_senha = ttk.Entry(card, show="•")
        self.txt_senha.grid(row=2, column=1, sticky="ew", pady=6, padx=(10, 0))

        ttk.Label(card, text="Perfil:", style="Card.TLabel").grid(row=3, column=0, sticky="w", pady=6)
        self.cb_perfil = ttk.Combobox(card, values=self.PERFIS, state="readonly")
        self.cb_perfil.current(0)
        self.cb_perfil.grid(row=3, column=1, sticky="ew", pady=6, padx=(10, 0))

        ttk.Label(card, text="Ativo:", style="Card.TLabel").grid(row=4, column=0, sticky="w", pady=6)
        self.var_ativo = tk.BooleanVar(value=True)
        ttk.Checkbutton(card, variable=self.var_ativo).grid(row=4, column=1, sticky="w", pady=6, padx=(10, 0))

        ttk.Label(card,
                  text=("ADMIN: acesso total (cadastros + operação + admins).\n"
                        "OPERADOR: apenas operação (simular acesso + histórico)."),
                  style="Card.TLabel", foreground=COR["mudo"],
                  font=("Helvetica", 9), justify="left").grid(
            row=5, column=0, columnspan=2, sticky="w", pady=(12, 0)
        )

        botoes = ttk.Frame(corpo, style="TFrame")
        botoes.pack(fill="x", pady=(12, 0))
        ttk.Button(botoes, text=("Atualizar" if admin_existente else "Salvar"),
                   style="Primary.TButton", command=self._salvar).pack(side="right")
        ttk.Button(botoes, text="Cancelar", command=self.destroy).pack(side="right", padx=(0, 8))

        self._preencher_edicao()

        self.lift()
        self.focus_force()
        self.after(120, self.txt_login.focus_set)

    # ------------------------------------------------------------------
    def _preencher_edicao(self):
        if not self.admin_existente:
            return
        a = self.admin_existente
        self.txt_login.insert(0, a.login)
        self.txt_login.config(state="disabled")  # login é chave natural
        self.txt_nome.insert(0, a.nome)
        self.cb_perfil.set(a.perfil.value)
        self.var_ativo.set(a.ativo)

    # ------------------------------------------------------------------
    def _salvar(self):
        login = self.txt_login.get().strip()
        nome  = self.txt_nome.get().strip()
        senha = self.txt_senha.get()
        perfil = self.cb_perfil.get()
        ativo  = self.var_ativo.get()

        if self.admin_existente:
            sucesso, msg = self.controller.atualizar_administrador(
                login, nome, perfil, ativo, nova_senha=senha
            )
        else:
            sucesso, msg = self.controller.salvar_administrador(
                login, nome, senha, perfil, ativo
            )

        if sucesso:
            messagebox.showinfo("Sucesso", msg, parent=self)
            self.destroy()
        else:
            messagebox.showerror("Erro", msg, parent=self)
