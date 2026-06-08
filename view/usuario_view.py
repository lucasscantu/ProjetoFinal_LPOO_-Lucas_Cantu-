"""
Cadastro/edição de Usuário. CPF é chave natural (bloqueado em edição) e
recebe validação de dígitos verificadores. Validade só se aplica a
Aluno/Visitante.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import messagebox, ttk

from control.usuario_controller import UsuarioController
from view.estilos import COR, criar_cabecalho


class JanelaCadastroUsuario(tk.Toplevel):
    TIPOS = ["Aluno", "Funcionario", "Visitante"]

    def __init__(self, master=None, usuario_existente=None):
        super().__init__(master)
        self.usuario_existente = usuario_existente
        self.controller = UsuarioController()

        modo = "Atualizar" if usuario_existente else "Cadastrar"
        self.title(f"{modo} Usuário")
        self.geometry("480x500")
        self.resizable(False, False)
        self.configure(bg=COR["fundo"])

        criar_cabecalho(self, f"{modo} Usuário",
                        "Aluno, Funcionário ou Visitante")
        self._criar_widgets()
        self._preencher_edicao()
        self._ao_trocar_tipo()

        self.lift()
        self.focus_force()
        self.after(120, self.txt_cpf.focus_set)

    # ------------------------------------------------------------------
    def _criar_widgets(self):
        corpo = ttk.Frame(self, style="TFrame", padding=(24, 16))
        corpo.pack(expand=True, fill="both")

        card = ttk.Frame(corpo, style="Card.TFrame", padding=18)
        card.pack(fill="both", expand=True)
        card.columnconfigure(1, weight=1)

        ttk.Label(card, text="CPF:", style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=6)
        self.txt_cpf = ttk.Entry(card)
        self.txt_cpf.grid(row=0, column=1, sticky="ew", pady=6, padx=(10, 0))

        ttk.Label(card, text="Nome:", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=6)
        self.txt_nome = ttk.Entry(card)
        self.txt_nome.grid(row=1, column=1, sticky="ew", pady=6, padx=(10, 0))

        ttk.Label(card, text="Tipo:", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=6)
        self.cb_tipo = ttk.Combobox(card, values=self.TIPOS, state="readonly")
        self.cb_tipo.current(0)
        self.cb_tipo.grid(row=2, column=1, sticky="ew", pady=6, padx=(10, 0))
        self.cb_tipo.bind("<<ComboboxSelected>>", self._ao_trocar_tipo)

        ttk.Label(card, text="Ativo:", style="Card.TLabel").grid(row=3, column=0, sticky="w", pady=6)
        self.var_ativo = tk.BooleanVar(value=True)
        ttk.Checkbutton(card, variable=self.var_ativo).grid(row=3, column=1, sticky="w", pady=6, padx=(10, 0))

        ttk.Label(card, text="Validade (dd/mm/aaaa):", style="Card.TLabel").grid(row=4, column=0, sticky="w", pady=6)
        self.txt_validade = ttk.Entry(card)
        self.txt_validade.grid(row=4, column=1, sticky="ew", pady=6, padx=(10, 0))

        self.lbl_dica = ttk.Label(card, text="", style="Card.TLabel",
                                  foreground=COR["mudo"], font=("Helvetica", 9))
        self.lbl_dica.grid(row=5, column=0, columnspan=2, sticky="w", pady=(8, 0))

        botoes = ttk.Frame(corpo, style="TFrame")
        botoes.pack(fill="x", pady=(12, 0))
        ttk.Button(botoes, text=("Atualizar" if self.usuario_existente else "Salvar"),
                   style="Primary.TButton", command=self._salvar).pack(side="right")
        ttk.Button(botoes, text="Cancelar",
                   command=self.destroy).pack(side="right", padx=(0, 8))

    # ------------------------------------------------------------------
    def _ao_trocar_tipo(self, _evt=None):
        if self.cb_tipo.get().lower().startswith("funcion"):
            self.txt_validade.config(state="disabled")
            self.lbl_dica.config(text="Funcionário não exige data de validade.")
        else:
            self.txt_validade.config(state="normal")
            self.lbl_dica.config(text="Aluno/Visitante: informe a validade do acesso.")

    def _preencher_edicao(self):
        if not self.usuario_existente:
            return
        u = self.usuario_existente
        self.txt_cpf.insert(0, u.cpf_formatado())
        self.txt_cpf.config(state="disabled")
        self.txt_nome.insert(0, u.nome)
        self.cb_tipo.set(u.tipo.value.capitalize())
        self.cb_tipo.config(state="disabled")
        self.var_ativo.set(u.ativo)
        if u.validade:
            self.txt_validade.insert(0, u.validade.strftime("%d/%m/%Y"))

    def _salvar(self):
        cpf = self.txt_cpf.get().strip()
        nome = self.txt_nome.get().strip()
        tipo = self.cb_tipo.get().strip()
        ativo = self.var_ativo.get()
        validade = "" if str(self.txt_validade["state"]) == "disabled" else self.txt_validade.get().strip()

        if self.usuario_existente:
            sucesso, msg = self.controller.atualizar_usuario(cpf, nome, tipo, ativo, validade)
        else:
            sucesso, msg = self.controller.salvar_usuario(cpf, nome, tipo, ativo, validade)

        if sucesso:
            messagebox.showinfo("Sucesso", msg, parent=self)
            self.destroy()
        else:
            messagebox.showerror("Erro", msg, parent=self)
