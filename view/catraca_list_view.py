"""Listagem de Catracas — CRUD + transição de estado (Manutenção)."""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox

from control.catraca_controller import CatracaController
from view.estilos import COR, criar_cabecalho, aplicar_zebra


class JanelaListagemCatracas(tk.Toplevel):
    """Listagem administrativa de catracas."""

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Catracas")
        self.geometry("760x460")
        self.configure(bg=COR["fundo"])
        self.controller = CatracaController()

        criar_cabecalho(self, "Catracas Cadastradas",
                        "Estado controlado pelo padrão State")
        self._criar_widgets()
        self.carregar_dados()

        self.lift()
        self.focus_force()

    def _criar_widgets(self):
        corpo = ttk.Frame(self, style="TFrame", padding=(20, 14))
        corpo.pack(expand=True, fill="both")

        frame_tree = ttk.Frame(corpo, style="TFrame")
        frame_tree.pack(expand=True, fill="both")
        scrollbar = ttk.Scrollbar(frame_tree)
        scrollbar.pack(side="right", fill="y")

        colunas = ("Código", "Localização", "Estado")
        self.tree = ttk.Treeview(frame_tree, columns=colunas, show="headings",
                                 yscrollcommand=scrollbar.set)
        larguras = {"Código": 130, "Localização": 380, "Estado": 150}
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=larguras[col])
        self.tree.pack(expand=True, fill="both")
        scrollbar.config(command=self.tree.yview)

        botoes = ttk.Frame(corpo, style="TFrame")
        botoes.pack(fill="x", pady=(12, 0))
        ttk.Button(botoes, text="Nova", style="Primary.TButton",
                   command=self.abrir_novo).pack(side="left", padx=(0, 6))
        ttk.Button(botoes, text="Editar",
                   command=self.abrir_editar).pack(side="left", padx=6)
        ttk.Button(botoes, text="Alternar Manutenção",
                   command=self.alternar_manutencao).pack(side="left", padx=6)
        ttk.Button(botoes, text="Remover", style="Danger.TButton",
                   command=self.remover).pack(side="left", padx=6)
        ttk.Button(botoes, text="Fechar",
                   command=self.destroy).pack(side="right")

    def carregar_dados(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        catracas = self.controller.listar_catracas()
        if catracas is None:
            messagebox.showerror("Erro", "Erro ao carregar catracas. Verifique a conexão com o banco.",
                                 parent=self)
            return
        for c in catracas:
            self.tree.insert("", "end", values=(c.codigo, c.localizacao, c.nome_estado()))
        aplicar_zebra(self.tree)

    def _codigo_selecionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma catraca.", parent=self)
            return None
        return self.tree.item(sel[0])["values"][0]

    def abrir_novo(self):
        from view.catraca_view import JanelaCadastroCatraca
        janela = JanelaCadastroCatraca(self)
        self.wait_window(janela)
        self.carregar_dados()

    def abrir_editar(self):
        codigo = self._codigo_selecionado()
        if not codigo:
            return
        catraca = self.controller.buscar_por_codigo(str(codigo))
        if not catraca:
            messagebox.showerror("Erro", "Catraca não encontrada.", parent=self)
            return
        from view.catraca_view import JanelaCadastroCatraca
        janela = JanelaCadastroCatraca(self, catraca_existente=catraca)
        self.wait_window(janela)
        self.carregar_dados()

    def alternar_manutencao(self):
        codigo = self._codigo_selecionado()
        if not codigo:
            return
        sucesso, msg = self.controller.alternar_manutencao(str(codigo))
        if sucesso:
            messagebox.showinfo("Estado da Catraca", msg, parent=self)
            self.carregar_dados()
        else:
            messagebox.showerror("Erro", msg, parent=self)

    def remover(self):
        codigo = self._codigo_selecionado()
        if not codigo:
            return
        if messagebox.askyesno("Confirmar", f"Remover a catraca {codigo}?", parent=self):
            sucesso, msg = self.controller.remover_catraca(str(codigo))
            if sucesso:
                messagebox.showinfo("Sucesso", msg, parent=self)
                self.carregar_dados()
            else:
                messagebox.showerror("Erro", msg, parent=self)
