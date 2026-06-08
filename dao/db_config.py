"""
Configuração de conexão com o PostgreSQL.

As credenciais podem ser sobrescritas por variáveis de ambiente, o que é
útil para não versionar senhas. Caso nada seja definido, usa os valores
padrão abaixo (compatíveis com uma instalação local típica do PostgreSQL).

Banco esperado (conforme enunciado): lpoo_projeto_catraca
"""

import os
import psycopg2
from psycopg2 import Error


class DatabaseConfig:
    @staticmethod
    def get_connection():
        try:
            conexao = psycopg2.connect(
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "postgres"),
                host=os.getenv("DB_HOST", "localhost"),
                port=os.getenv("DB_PORT", "5432"),
                database=os.getenv("DB_NAME", "lpoo_projeto_catraca"),
            )
            return conexao
        except Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return None
