"""
Janela de Login — controla o acesso à aplicação. Roda como uma tk.Tk
própria; ao autenticar com sucesso, fecha a si mesma e abre a janela
principal. O administrador autenticado fica disponível em
`model.sessao.sessao_atual`.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox

from control.administrador_controller import AdministradorController
from view.estilos import aplicar_tema, COR


class JanelaLogin(tk.Tk):
    """Tela de autenticação inicial do sistema."""

    def __init__(self):
        super().__init__()
        self.title("Login — Sistema de Catraca Eletrônica")
        self.geometry("420x420")
        self.resizable(False, False)
        self.configure(bg=COR["fundo"])

        aplicar_tema(self)
        self.controller = AdministradorController()
        self._sucesso = False  # consultado pelo main após mainloop()

        self._criar_widgets()

        # Centraliza a janela na tela
        self.update_idletasks()
        w, h = 420, 420
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.protocol("WM_DELETE_WINDOW", self._cancelar)
        self.bind("<Return>", lambda _e: self._entrar())
        self.after(120, self.txt_login.focus_set)

    # ------------------------------------------------------------------
    def _criar_widgets(self):
        # Cabeçalho colorido
        cab = tk.Frame(self, bg=COR["primaria"])
        cab.pack(fill="x")
        ttk.Label(cab, text="🛂  Catraca Eletrônica",
                  style="Titulo.TLabel").pack(anchor="center", pady=(0, 0))
        ttk.Label(cab, text="Acesso ao Sistema",
                  style="Subtitulo.TLabel").pack(anchor="center")

        # Card central com o formulário
        wrapper = ttk.Frame(self, style="TFrame", padding=(30, 22))
        wrapper.pack(expand=True, fill="both")

        card = ttk.Frame(wrapper, style="Card.TFrame", padding=22)
        card.pack(expand=True, fill="both")

        ttk.Label(card, text="Entrar", style="Card.TLabel",
                  font=("Helvetica", 14, "bold")).pack(anchor="w", pady=(0, 12))

        ttk.Label(card, text="Login:", style="Card.TLabel").pack(anchor="w")
        self.txt_login = ttk.Entry(card)
        self.txt_login.pack(fill="x", pady=(2, 12))

        ttk.Label(card, text="Senha:", style="Card.TLabel").pack(anchor="w")
        self.txt_senha = ttk.Entry(card, show="•")
        self.txt_senha.pack(fill="x", pady=(2, 16))

        self.lbl_erro = ttk.Label(card, text="", style="Card.TLabel",
                                  foreground=COR["perigo"])
        self.lbl_erro.pack(anchor="w")

        botoes = ttk.Frame(card, style="Card.TFrame")
        botoes.pack(fill="x", pady=(8, 0))
        ttk.Button(botoes, text="Entrar", style="Primary.TButton",
                   command=self._entrar).pack(side="right")
        ttk.Button(botoes, text="Cancelar",
                   command=self._cancelar).pack(side="right", padx=(0, 8))

        # Dica do administrador padrão (só para uso acadêmico)
        ttk.Label(self,
                  text="Credenciais padrão:  admin  /  admin123",
                  style="Mudo.TLabel").pack(pady=(0, 10))

    # ------------------------------------------------------------------
    def _entrar(self):
        login = self.txt_login.get().strip()
        senha = self.txt_senha.get()
        sucesso, msg, _adm = self.controller.autenticar(login, senha)

        if sucesso:
            self._sucesso = True
            self.destroy()
        else:
            self.lbl_erro.config(text=msg)
            self.txt_senha.delete(0, "end")
            self.txt_senha.focus_set()

    def _cancelar(self):
        self._sucesso = False
        self.destroy()

    # ------------------------------------------------------------------
    @property
    def autenticado(self) -> bool:
        return self._sucesso
