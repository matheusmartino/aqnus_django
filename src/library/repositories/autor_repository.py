"""
library.repositories.autor_repository

Acesso a dados da entidade Autor.
"""

from library.models import Autor


class AutorRepository:

    @staticmethod
    def listar_ativos():
        return Autor.objects.filter(ativo=True)

    @staticmethod
    def buscar_por_nome(nome):
        return Autor.objects.filter(nome__icontains=nome, ativo=True)
