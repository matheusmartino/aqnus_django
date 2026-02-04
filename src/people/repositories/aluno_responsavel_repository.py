"""
people.repositories.aluno_responsavel_repository

Acesso a dados da entidade AlunoResponsavel.
"""

from people.models import AlunoResponsavel


class AlunoResponsavelRepository:

    @staticmethod
    def listar_por_aluno(aluno):
        return AlunoResponsavel.objects.filter(
            aluno=aluno,
        ).select_related('responsavel__pessoa')

    @staticmethod
    def listar_por_responsavel(responsavel):
        return AlunoResponsavel.objects.filter(
            responsavel=responsavel,
        ).select_related('aluno__pessoa')
