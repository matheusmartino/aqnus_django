"""
library.repositories.editora_repository

Acesso a dados da entidade Editora.
"""

from library.models import Editora


class EditoraRepository:

    @staticmethod
    def listar_ativas():
        return Editora.objects.filter(ativo=True)

    @staticmethod
    def buscar_por_nome(nome):
        return Editora.objects.filter(nome__icontains=nome, ativo=True)
