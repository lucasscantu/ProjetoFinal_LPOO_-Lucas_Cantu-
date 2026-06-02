"""
Padrão de Projeto: DAO (Data Access Object).

``GenericDAO`` define o contrato CRUD que todos os DAOs concretos devem
implementar, separando completamente as regras de acesso a dados do restante
da aplicação (model / controller / view).
"""

from abc import ABC, abstractmethod


class GenericDAO(ABC):
    @abstractmethod
    def salvar(self, objeto):
        pass

    @abstractmethod
    def listar_todos(self):
        pass

    @abstractmethod
    def remover(self, id_objeto):
        pass

    @abstractmethod
    def atualizar(self, objeto):
        pass
