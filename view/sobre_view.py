"""Tela 'Sobre' com a descrição do sistema e os dados do autor."""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk

from view.estilos import COR, criar_cabecalho


class JanelaSobre(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Sobre o Sistema")
        self.geometry("560x520")
        self.resizable(False, False)
        self.configure(bg=COR["fundo"])

        criar_cabecalho(self, "Sobre o Sistema",
                        "Catraca Eletrônica — LPOO 2026/1")

        corpo = ttk.Frame(self, style="TFrame", padding=(24, 18))
        corpo.pack(expand=True, fill="both")

        card = ttk.Frame(corpo, style="Card.TFrame", padding=20)
        card.pack(expand=True, fill="both")

        texto = (
            "Sistema de controle de acesso por catracas eletrônicas,\n"
            "desenvolvido para a Atividade Integradora Final da disciplina\n"
            "de Linguagem de Programação Orientada a Objetos (LPOO).\n\n"
            "Permite cadastrar usuários (alunos, funcionários e visitantes)\n"
            "e catracas, e simular passagens, registrando cada tentativa de\n"
            "acesso (autorizada ou negada) em um histórico consultável.\n\n"
            "Arquitetura:  MVC + DAO\n"
            "Persistência:  PostgreSQL\n\n"
            "Padrões de Projeto:\n"
            "   • DAO       — isolamento do acesso a dados\n"
            "   • Factory   — criação dos tipos de usuário\n"
            "   • State     — estados da catraca\n"
            "   • Strategy  — regra de autorização por tipo de usuário\n\n"
            "Controle de acesso ao sistema:\n"
            "   • ADMIN     — acesso total\n"
            "   • OPERADOR  — apenas simular acesso e consultar histórico\n\n"
            "Autor: Lucas Cantú\n"
            "Curso: Bacharelado em Ciência da Computação\n"
            "Professora: Vanessa Lago Machado"
        )
        ttk.Label(card, text=texto, style="Card.TLabel",
                  justify="left", font=("Helvetica", 10)).pack(anchor="w")

        ttk.Button(corpo, text="Fechar", style="Primary.TButton",
                   command=self.destroy).pack(pady=(12, 0))

        self.lift()
        self.focus_force()
