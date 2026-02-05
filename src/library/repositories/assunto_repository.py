"""
library.repositories.assunto_repository

Acesso a dados da entidade Assunto.
"""

from library.models import Assunto


class AssuntoRepository:

    @staticmethod
    def listar_ativos():
        return Assunto.objects.filter(ativo=True)

    @staticmethod
    def buscar_por_nome(nome):
        return Assunto.objects.filter(nome__icontains=nome, ativo=True)
