"""
Tela operacional da catraca. Acesso permitido a qualquer perfil autenticado
(ADMIN ou OPERADOR). Combina os padrões State (catraca) e Strategy (regra
por tipo de usuário) e registra cada tentativa no histórico.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox

from control.acesso_controller import AcessoController
from control.usuario_controller import UsuarioController
from control.catraca_controller import CatracaController
from view.estilos import COR, criar_cabecalho


class JanelaSimularAcesso(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Simular Acesso")
        self.geometry("520x500")
        self.resizable(False, False)
        self.configure(bg=COR["fundo"])

        self.acesso_ctrl = AcessoController()
        self.usuario_ctrl = UsuarioController()
        self.catraca_ctrl = CatracaController()

        criar_cabecalho(self, "Simulação de Passagem",
                        "State (catraca) + Strategy (tipo de usuário)")
        self._criar_widgets()
        self._carregar_combos()

        self.lift()
        self.focus_force()

    def _criar_widgets(self):
        corpo = ttk.Frame(self, style="TFrame", padding=(24, 16))
        corpo.pack(expand=True, fill="both")

        card = ttk.Frame(corpo, style="Card.TFrame", padding=18)
        card.pack(fill="x")
        card.columnconfigure(1, weight=1)

        ttk.Label(card, text="Usuário:", style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=8)
        self.cb_usuario = ttk.Combobox(card, state="readonly")
        self.cb_usuario.grid(row=0, column=1, sticky="ew", pady=8, padx=(10, 0))

        ttk.Label(card, text="Catraca:", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=8)
        self.cb_catraca = ttk.Combobox(card, state="readonly")
        self.cb_catraca.grid(row=1, column=1, sticky="ew", pady=8, padx=(10, 0))

        ttk.Label(card, text="Sentido:", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=8)
        self.cb_tipo = ttk.Combobox(card, values=["ENTRADA", "SAIDA"], state="readonly")
        self.cb_tipo.current(0)
        self.cb_tipo.grid(row=2, column=1, sticky="ew", pady=8, padx=(10, 0))

        ttk.Button(corpo, text="▶  Validar e Registrar Passagem",
                   style="Primary.TButton", command=self._processar).pack(pady=(14, 8), fill="x")

        # Painel de resultado destacado
        self.resultado_frame = tk.Frame(corpo, bg=COR["fundo"],
                                        highlightthickness=2,
                                        highlightbackground=COR["borda"])
        self.resultado_frame.pack(fill="x", pady=8)
        self.lbl_resultado = tk.Label(
            self.resultado_frame, text="Aguardando simulação…",
            bg=COR["fundo"], fg=COR["mudo"],
            font=("Helvetica", 13, "bold"),
            wraplength=460, justify="center", padx=12, pady=14,
        )
        self.lbl_resultado.pack(fill="x")

        botoes = ttk.Frame(corpo, style="TFrame")
        botoes.pack(fill="x", pady=(8, 0))
        ttk.Button(botoes, text="Atualizar listas",
                   command=self._carregar_combos).pack(side="left")
        ttk.Button(botoes, text="Fechar",
                   command=self.destroy).pack(side="right")

    def _carregar_combos(self):
        self._usuarios = self.usuario_ctrl.listar_usuarios() or []
        self._catracas = self.catraca_ctrl.listar_catracas() or []

        self.cb_usuario["values"] = [
            f"{u.nome} — {u.cpf_formatado()} ({u.tipo.value})" for u in self._usuarios
        ]
        self.cb_catraca["values"] = [
            f"{c.codigo} — {c.localizacao} [{c.nome_estado()}]" for c in self._catracas
        ]
        if self._usuarios:
            self.cb_usuario.current(0)
        if self._catracas:
            self.cb_catraca.current(0)

    def _processar(self):
        iu = self.cb_usuario.current()
        ic = self.cb_catraca.current()
        if iu < 0 or ic < 0:
            messagebox.showwarning("Aviso",
                                   "Cadastre e selecione um usuário e uma catraca.",
                                   parent=self)
            return

        cpf = self._usuarios[iu].cpf
        codigo = self._catracas[ic].codigo
        tipo = self.cb_tipo.get()

        autorizado, motivo = self.acesso_ctrl.processar_acesso(cpf, codigo, tipo)

        if autorizado:
            cor = COR["sucesso"]
            texto = f"✅  ACESSO LIBERADO\n{motivo}"
        else:
            cor = COR["perigo"]
            texto = f"⛔  ACESSO NEGADO\n{motivo}"

        self.lbl_resultado.config(text=texto, fg=cor)
        self.resultado_frame.config(highlightbackground=cor, bg=COR["fundo"])
        self.lbl_resultado.config(bg=COR["fundo"])

        # reflete eventual mudança de estado da catraca
        self._carregar_combos()
