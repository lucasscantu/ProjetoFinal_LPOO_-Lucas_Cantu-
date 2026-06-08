"""
Histórico de Acessos com filtros (resultado + CPF).
Acesso permitido a qualquer perfil autenticado.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox

from control.acesso_controller import AcessoController
from view.estilos import COR, criar_cabecalho, aplicar_zebra


class JanelaListagemAcessos(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Histórico de Acessos")
        self.geometry("960x520")
        self.configure(bg=COR["fundo"])
        self.controller = AcessoController()

        criar_cabecalho(self, "Histórico de Acessos",
                        "Filtros por resultado e CPF")
        self._criar_widgets()
        self.aplicar_filtro()

        self.lift()
        self.focus_force()

    def _criar_widgets(self):
        corpo = ttk.Frame(self, style="TFrame", padding=(20, 14))
        corpo.pack(expand=True, fill="both")

        # ----- Filtros -----
        filtros = ttk.Frame(corpo, style="TFrame")
        filtros.pack(fill="x", pady=(0, 8))
        ttk.Label(filtros, text="Resultado:").pack(side="left")
        self.cb_resultado = ttk.Combobox(filtros, values=["TODOS", "AUTORIZADO", "NEGADO"],
                                         state="readonly", width=14)
        self.cb_resultado.current(0)
        self.cb_resultado.pack(side="left", padx=8)
        ttk.Label(filtros, text="CPF:").pack(side="left", padx=(10, 0))
        self.txt_cpf = ttk.Entry(filtros, width=22)
        self.txt_cpf.pack(side="left", padx=8)
        self.txt_cpf.bind("<Return>", lambda e: self.aplicar_filtro())
        ttk.Button(filtros, text="Filtrar", style="Primary.TButton",
                   command=self.aplicar_filtro).pack(side="left", padx=4)
        ttk.Button(filtros, text="Limpar",
                   command=self.limpar_filtro).pack(side="left")

        # ----- Tabela -----
        frame_tree = ttk.Frame(corpo, style="TFrame")
        frame_tree.pack(expand=True, fill="both")
        scrollbar = ttk.Scrollbar(frame_tree)
        scrollbar.pack(side="right", fill="y")

        colunas = ("ID", "Data/Hora", "Usuário", "CPF", "Catraca", "Sentido", "Resultado")
        self.tree = ttk.Treeview(frame_tree, columns=colunas, show="headings",
                                 yscrollcommand=scrollbar.set)
        larguras = {"ID": 60, "Data/Hora": 150, "Usuário": 190, "CPF": 140,
                    "Catraca": 100, "Sentido": 100, "Resultado": 120}
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=larguras[col])
        self.tree.pack(expand=True, fill="both")
        scrollbar.config(command=self.tree.yview)

        # ----- Botões -----
        botoes = ttk.Frame(corpo, style="TFrame")
        botoes.pack(fill="x", pady=(12, 0))
        ttk.Button(botoes, text="Ver Detalhes", style="Primary.TButton",
                   command=self.ver_detalhes).pack(side="left", padx=(0, 6))
        ttk.Button(botoes, text="Remover", style="Danger.TButton",
                   command=self.remover).pack(side="left", padx=6)
        ttk.Button(botoes, text="Fechar",
                   command=self.destroy).pack(side="right")

    def aplicar_filtro(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        resultado = self.cb_resultado.get()
        cpf = self.txt_cpf.get().strip()
        self._acessos = self.controller.filtrar_acessos(resultado, cpf)
        for a in self._acessos:
            self.tree.insert("", "end", values=(
                a.id,
                a.data_hora.strftime("%d/%m/%Y %H:%M"),
                a.usuario.nome,
                a.usuario.cpf_formatado(),
                a.catraca.codigo,
                a.tipo.value,
                "AUTORIZADO" if a.autorizado else "NEGADO",
            ))
        aplicar_zebra(self.tree)

    def limpar_filtro(self):
        self.cb_resultado.current(0)
        self.txt_cpf.delete(0, "end")
        self.aplicar_filtro()

    def _acesso_selecionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um registro.", parent=self)
            return None
        id_sel = self.tree.item(sel[0])["values"][0]
        return next((a for a in self._acessos if a.id == id_sel), None)

    def ver_detalhes(self):
        acesso = self._acesso_selecionado()
        if acesso:
            messagebox.showinfo("Detalhes do Acesso", acesso.exibir_dados(), parent=self)

    def remover(self):
        acesso = self._acesso_selecionado()
        if not acesso:
            return
        if messagebox.askyesno("Confirmar", f"Remover o acesso ID {acesso.id}?", parent=self):
            sucesso, msg = self.controller.remover_acesso(acesso.id)
            if sucesso:
                messagebox.showinfo("Sucesso", msg, parent=self)
                self.aplicar_filtro()
            else:
                messagebox.showerror("Erro", msg, parent=self)
