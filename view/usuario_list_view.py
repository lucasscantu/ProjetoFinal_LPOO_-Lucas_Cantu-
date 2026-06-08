"""
Listagem de Usuários — busca por nome/CPF, CRUD completo.
Acesso restrito a ADMIN (gateado também pelo menu da janela principal).
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox

from control.usuario_controller import UsuarioController
from view.estilos import COR, criar_cabecalho, aplicar_zebra


class JanelaListagemUsuarios(tk.Toplevel):
    """Tela administrativa de usuários do sistema."""

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Usuários")
        self.geometry("840x500")
        self.configure(bg=COR["fundo"])
        self.controller = UsuarioController()

        criar_cabecalho(self, "Usuários Cadastrados",
                        "Alunos, Funcionários e Visitantes")
        self._criar_widgets()
        self.carregar_dados()

        self.lift()
        self.focus_force()

    # ------------------------------------------------------------------
    def _criar_widgets(self):
        corpo = ttk.Frame(self, style="TFrame", padding=(20, 14))
        corpo.pack(expand=True, fill="both")

        # ----- Barra de busca -----
        busca = ttk.Frame(corpo, style="TFrame")
        busca.pack(fill="x", pady=(0, 8))
        ttk.Label(busca, text="Buscar (nome ou CPF):").pack(side="left")
        self.txt_busca = ttk.Entry(busca, width=32)
        self.txt_busca.pack(side="left", padx=8)
        self.txt_busca.bind("<Return>", lambda e: self.aplicar_filtro())
        ttk.Button(busca, text="Buscar", style="Primary.TButton",
                   command=self.aplicar_filtro).pack(side="left", padx=4)
        ttk.Button(busca, text="Limpar",
                   command=self.limpar_filtro).pack(side="left")

        # ----- Tabela -----
        frame_tree = ttk.Frame(corpo, style="TFrame")
        frame_tree.pack(expand=True, fill="both")
        scrollbar = ttk.Scrollbar(frame_tree)
        scrollbar.pack(side="right", fill="y")

        colunas = ("CPF", "Nome", "Tipo", "Ativo", "Validade")
        self.tree = ttk.Treeview(frame_tree, columns=colunas, show="headings",
                                 yscrollcommand=scrollbar.set)
        larguras = {"CPF": 140, "Nome": 260, "Tipo": 110, "Ativo": 70, "Validade": 110}
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=larguras[col])
        self.tree.pack(expand=True, fill="both")
        scrollbar.config(command=self.tree.yview)

        # ----- Botões -----
        botoes = ttk.Frame(corpo, style="TFrame")
        botoes.pack(fill="x", pady=(12, 0))
        ttk.Button(botoes, text="Novo", style="Primary.TButton",
                   command=self.abrir_novo).pack(side="left", padx=(0, 6))
        ttk.Button(botoes, text="Editar",
                   command=self.abrir_editar).pack(side="left", padx=6)
        ttk.Button(botoes, text="Ver Detalhes",
                   command=self.mostrar_info).pack(side="left", padx=6)
        ttk.Button(botoes, text="Remover", style="Danger.TButton",
                   command=self.remover).pack(side="left", padx=6)
        ttk.Button(botoes, text="Fechar",
                   command=self.destroy).pack(side="right")

    # ------------------------------------------------------------------
    def _inserir_linhas(self, usuarios):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for u in usuarios:
            validade = u.validade.strftime("%d/%m/%Y") if u.validade else "—"
            self.tree.insert("", "end", values=(
                u.cpf_formatado(), u.nome, u.tipo.value,
                "Sim" if u.ativo else "Não", validade,
            ))
        aplicar_zebra(self.tree)

    def carregar_dados(self):
        usuarios = self.controller.listar_usuarios()
        if usuarios is None:
            messagebox.showerror("Erro", "Erro ao carregar usuários. Verifique a conexão com o banco.",
                                 parent=self)
            return
        self._inserir_linhas(usuarios)

    def aplicar_filtro(self):
        termo = self.txt_busca.get().strip()
        self._inserir_linhas(self.controller.filtrar_usuarios(termo))

    def limpar_filtro(self):
        self.txt_busca.delete(0, "end")
        self.carregar_dados()

    def _cpf_selecionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um usuário.", parent=self)
            return None
        return self.tree.item(sel[0])["values"][0]

    # ------------------------------------------------------------------
    def abrir_novo(self):
        from view.usuario_view import JanelaCadastroUsuario
        janela = JanelaCadastroUsuario(self)
        self.wait_window(janela)
        self.carregar_dados()

    def abrir_editar(self):
        cpf = self._cpf_selecionado()
        if not cpf:
            return
        usuario = self.controller.buscar_por_cpf(str(cpf))
        if not usuario:
            messagebox.showerror("Erro", "Usuário não encontrado.", parent=self)
            return
        from view.usuario_view import JanelaCadastroUsuario
        janela = JanelaCadastroUsuario(self, usuario_existente=usuario)
        self.wait_window(janela)
        self.carregar_dados()

    def mostrar_info(self):
        cpf = self._cpf_selecionado()
        if not cpf:
            return
        usuario = self.controller.buscar_por_cpf(str(cpf))
        if usuario:
            messagebox.showinfo("Informações do Usuário", usuario.exibir_dados(), parent=self)
        else:
            messagebox.showerror("Erro", "Usuário não encontrado.", parent=self)

    def remover(self):
        cpf = self._cpf_selecionado()
        if not cpf:
            return
        if messagebox.askyesno("Confirmar", f"Remover o usuário de CPF {cpf}?", parent=self):
            sucesso, msg = self.controller.remover_usuario(str(cpf))
            if sucesso:
                messagebox.showinfo("Sucesso", msg, parent=self)
                self.carregar_dados()
            else:
                messagebox.showerror("Erro", msg, parent=self)
