"""
Ponto de entrada do Sistema de Catraca Eletrônica.

Fluxo:
    1. Abre a Janela de Login. Encerra o programa se o usuário cancelar.
    2. Após login bem-sucedido, abre a Janela Principal.
    3. Se o usuário fizer logout, volta para a tela de login.
       "Encerrar Aplicação" finaliza o processo imediatamente.
"""
import sys
import os

# Garante que os pacotes (model, dao, control, view) sejam encontrados
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from view.login_view import JanelaLogin
from view.janela_principal import JanelaPrincipal
from model.sessao import sessao_atual


def main():
    while True:
        # Etapa 1: autenticação
        login = JanelaLogin()
        login.mainloop()
        if not login.autenticado:
            break  # usuário cancelou o login

        # Etapa 2: aplicação principal
        app = JanelaPrincipal()
        app.mainloop()

        # Etapa 3: se a sessão foi encerrada (logout), reabre o login.
        # Caso contrário (fechamento da janela), encerra a aplicação.
        if sessao_atual.autenticado:
            sessao_atual.logout()
            break


if __name__ == "__main__":
    main()
