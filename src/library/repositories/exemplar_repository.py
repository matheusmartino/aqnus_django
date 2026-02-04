"""
library.repositories.exemplar_repository

Acesso a dados da entidade Exemplar.
"""

from library.models import Exemplar


class ExemplarRepository:

    @staticmethod
    def listar_por_obra(obra):
        return Exemplar.objects.filter(
            obra=obra,
            ativo=True,
        ).select_related('obra')

    @staticmethod
    def listar_disponiveis():
        return Exemplar.objects.filter(
            situacao=Exemplar.Situacao.DISPONIVEL,
            ativo=True,
        ).select_related('obra')

    @staticmethod
    def buscar_por_codigo(codigo_patrimonio):
        return Exemplar.objects.filter(
            codigo_patrimonio=codigo_patrimonio,
        ).select_related('obra').first()
