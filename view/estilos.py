"""
Estilos visuais da aplicação — paleta de cores, tipografia e estilos ttk
nomeados. Centraliza a aparência para que todas as telas tenham um visual
consistente.

Uso:
    from view.estilos import aplicar_tema, COR, criar_cabecalho

    class MinhaJanela(tk.Toplevel):
        def __init__(self, master):
            super().__init__(master)
            self.configure(bg=COR["fundo"])
            criar_cabecalho(self, "Título da tela")
            ttk.Button(self, text="Salvar", style="Primary.TButton")
"""
from tkinter import ttk
import tkinter as tk


# ---------------------------------------------------------------------------
# Paleta de cores (pensada como "tokens de design")
# ---------------------------------------------------------------------------
COR = {
    "fundo":       "#f3f5f9",   # fundo geral das janelas
    "superficie":  "#ffffff",   # áreas de conteúdo (cards, formulários)
    "primaria":    "#1f4f8b",   # cabeçalhos e botão principal
    "primaria_h":  "#2861a8",   # primária em hover
    "sucesso":     "#1b7f3b",   # botão / mensagem de sucesso
    "perigo":      "#b00020",   # botão / mensagem de erro
    "neutro":      "#5a6477",   # botões secundários
    "texto":       "#1a202c",   # texto padrão
    "texto_claro": "#ffffff",   # texto sobre fundos escuros
    "mudo":        "#6b7280",   # textos auxiliares / dicas
    "borda":       "#cfd6e0",   # bordas suaves
    "linha_zebra": "#f5f8fc",   # linhas alternadas em tabelas
}

# Tipografia
FONTE_TITULO    = ("Helvetica", 18, "bold")
FONTE_SUBTITULO = ("Helvetica", 11)
FONTE_PADRAO    = ("Helvetica", 10)
FONTE_BOTAO     = ("Helvetica", 10, "bold")
FONTE_TABELA    = ("Helvetica", 10)


# ---------------------------------------------------------------------------
def aplicar_tema(root: tk.Misc):
    """
    Aplica o tema visual à aplicação. Deve ser chamado uma única vez na
    janela raiz (tk.Tk) — todas as Toplevel filhas herdam os estilos.
    """
    style = ttk.Style(root)
    # 'clam' é o tema ttk mais customizável e funciona em todas as plataformas
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass  # mantém o tema padrão se 'clam' não estiver disponível

    # ----- Frames e Labels -----
    style.configure("TFrame", background=COR["fundo"])
    style.configure("Card.TFrame", background=COR["superficie"], relief="flat")

    style.configure("TLabel",
                    background=COR["fundo"], foreground=COR["texto"],
                    font=FONTE_PADRAO)
    style.configure("Card.TLabel",
                    background=COR["superficie"], foreground=COR["texto"],
                    font=FONTE_PADRAO)
    style.configure("Titulo.TLabel",
                    background=COR["primaria"], foreground=COR["texto_claro"],
                    font=FONTE_TITULO, padding=(20, 14))
    style.configure("Subtitulo.TLabel",
                    background=COR["primaria"], foreground="#dbe6f3",
                    font=FONTE_SUBTITULO, padding=(20, 0, 20, 12))
    style.configure("Mudo.TLabel",
                    background=COR["fundo"], foreground=COR["mudo"],
                    font=(FONTE_PADRAO[0], 9))
    style.configure("Status.TLabel",
                    background="#dde4ee", foreground=COR["texto"],
                    font=(FONTE_PADRAO[0], 9), padding=(10, 4))

    # ----- Entries e Combobox -----
    style.configure("TEntry", padding=4, fieldbackground=COR["superficie"])
    style.configure("TCombobox", padding=3, fieldbackground=COR["superficie"])

    # ----- Botões -----
    style.configure("TButton",
                    font=FONTE_BOTAO, padding=(14, 7),
                    background=COR["neutro"], foreground=COR["texto_claro"],
                    borderwidth=0)
    style.map("TButton",
              background=[("active", "#717b8e"), ("disabled", "#aab2c0")])

    style.configure("Primary.TButton",
                    font=FONTE_BOTAO, padding=(14, 7),
                    background=COR["primaria"], foreground=COR["texto_claro"],
                    borderwidth=0)
    style.map("Primary.TButton",
              background=[("active", COR["primaria_h"]), ("disabled", "#a4b5cb")])

    style.configure("Success.TButton",
                    font=FONTE_BOTAO, padding=(14, 7),
                    background=COR["sucesso"], foreground=COR["texto_claro"],
                    borderwidth=0)
    style.map("Success.TButton",
              background=[("active", "#249649"), ("disabled", "#9bc7a9")])

    style.configure("Danger.TButton",
                    font=FONTE_BOTAO, padding=(14, 7),
                    background=COR["perigo"], foreground=COR["texto_claro"],
                    borderwidth=0)
    style.map("Danger.TButton",
              background=[("active", "#cc1233"), ("disabled", "#daa1ad")])

    # ----- Treeview (tabelas) -----
    style.configure("Treeview",
                    background=COR["superficie"],
                    fieldbackground=COR["superficie"],
                    foreground=COR["texto"],
                    rowheight=24,
                    font=FONTE_TABELA,
                    bordercolor=COR["borda"],
                    borderwidth=1)
    style.configure("Treeview.Heading",
                    background=COR["primaria"],
                    foreground=COR["texto_claro"],
                    font=(FONTE_PADRAO[0], 10, "bold"),
                    padding=6,
                    relief="flat")
    style.map("Treeview.Heading",
              background=[("active", COR["primaria_h"])])
    style.map("Treeview",
              background=[("selected", "#cfdef6")],
              foreground=[("selected", COR["texto"])])

    return style


# ---------------------------------------------------------------------------
def criar_cabecalho(parent: tk.Misc, titulo: str, subtitulo: str = ""):
    """
    Cria a faixa colorida de cabeçalho no topo de uma janela, com título
    em destaque e subtítulo opcional. Retorna o frame para customização.
    """
    cabecalho = tk.Frame(parent, bg=COR["primaria"])
    cabecalho.pack(fill="x")
    ttk.Label(cabecalho, text=titulo, style="Titulo.TLabel").pack(
        anchor="w", padx=0, pady=(0, 0)
    )
    if subtitulo:
        ttk.Label(cabecalho, text=subtitulo, style="Subtitulo.TLabel").pack(
            anchor="w"
        )
    return cabecalho


def aplicar_zebra(tree: ttk.Treeview):
    """Configura as tags de cores alternadas para um Treeview já populado."""
    tree.tag_configure("par",   background=COR["superficie"])
    tree.tag_configure("impar", background=COR["linha_zebra"])
    for i, item in enumerate(tree.get_children()):
        tree.item(item, tags=("par" if i % 2 == 0 else "impar",))
