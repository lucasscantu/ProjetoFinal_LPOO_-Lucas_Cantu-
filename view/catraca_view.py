"""Cadastro/edição de catraca. Em edição o código fica bloqueado."""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox

from control.catraca_controller import CatracaController
from view.estilos import COR, criar_cabecalho


class JanelaCadastroCatraca(tk.Toplevel):
    def __init__(self, master=None, catraca_existente=None):
        super().__init__(master)
        self.catraca_existente = catraca_existente
        self.controller = CatracaController()

        modo = "Atualizar" if catraca_existente else "Cadastrar"
        self.title(f"{modo} Catraca")
        self.geometry("440x340")
        self.resizable(False, False)
        self.configure(bg=COR["fundo"])

        criar_cabecalho(self, f"{modo} Catraca",
                        "Formato do código: CAT-NN (ex.: CAT-01)")
        self._criar_widgets()

        if catraca_existente:
            self.txt_codigo.insert(0, catraca_existente.codigo)
            self.txt_codigo.config(state="disabled")
            self.txt_local.insert(0, catraca_existente.localizacao)

        self.lift()
        self.focus_force()
        self.after(120, self.txt_codigo.focus_set)

    def _criar_widgets(self):
        corpo = ttk.Frame(self, style="TFrame", padding=(24, 16))
        corpo.pack(expand=True, fill="both")

        card = ttk.Frame(corpo, style="Card.TFrame", padding=18)
        card.pack(fill="both", expand=True)
        card.columnconfigure(1, weight=1)

        ttk.Label(card, text="Código (ex.: CAT-01):", style="Card.TLabel").grid(
            row=0, column=0, sticky="w", pady=8
        )
        self.txt_codigo = ttk.Entry(card)
        self.txt_codigo.grid(row=0, column=1, sticky="ew", pady=8, padx=(10, 0))

        ttk.Label(card, text="Localização:", style="Card.TLabel").grid(
            row=1, column=0, sticky="w", pady=8
        )
        self.txt_local = ttk.Entry(card)
        self.txt_local.grid(row=1, column=1, sticky="ew", pady=8, padx=(10, 0))

        botoes = ttk.Frame(corpo, style="TFrame")
        botoes.pack(fill="x", pady=(12, 0))
        ttk.Button(botoes, text=("Atualizar" if self.catraca_existente else "Salvar"),
                   style="Primary.TButton", command=self._salvar).pack(side="right")
        ttk.Button(botoes, text="Cancelar",
                   command=self.destroy).pack(side="right", padx=(0, 8))

    def _salvar(self):
        codigo = self.txt_codigo.get().strip()
        local = self.txt_local.get().strip()

        if self.catraca_existente:
            sucesso, msg = self.controller.atualizar_catraca(codigo, local)
        else:
            sucesso, msg = self.controller.salvar_catraca(codigo, local)

        if sucesso:
            messagebox.showinfo("Sucesso", msg, parent=self)
            self.destroy()
        else:
            messagebox.showerror("Erro", msg, parent=self)
