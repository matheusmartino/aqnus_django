"""
academic.repositories.turma_repository

Acesso a dados da entidade Turma.
"""

from academic.models import Turma


class TurmaRepository:

    @staticmethod
    def listar_por_ano_letivo(ano_letivo):
        return Turma.objects.filter(
            ano_letivo=ano_letivo, ativa=True,
        ).select_related('escola', 'ano_letivo')

    @staticmethod
    def listar_por_escola(escola):
        return Turma.objects.filter(
            escola=escola, ativa=True,
        ).select_related('ano_letivo')
