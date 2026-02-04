"""
people.repositories.responsavel_repository

Acesso a dados da entidade Responsavel.
"""

from people.models import Responsavel


class ResponsavelRepository:

    @staticmethod
    def listar_ativos():
        return Responsavel.objects.filter(ativo=True).select_related('pessoa')

    @staticmethod
    def buscar_por_pessoa(pessoa):
        return Responsavel.objects.filter(pessoa=pessoa).select_related('pessoa').first()
