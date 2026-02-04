"""
academic.repositories.ano_letivo_repository

Acesso a dados da entidade AnoLetivo.
"""

from academic.models import AnoLetivo


class AnoLetivoRepository:

    @staticmethod
    def obter_ativo():
        return AnoLetivo.objects.filter(ativo=True).first()

    @staticmethod
    def listar_todos():
        return AnoLetivo.objects.all()
