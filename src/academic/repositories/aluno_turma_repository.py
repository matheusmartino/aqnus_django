"""
academic.repositories.aluno_turma_repository

Acesso a dados da entidade AlunoTurma.
"""

from academic.models import AlunoTurma


class AlunoTurmaRepository:

    @staticmethod
    def listar_por_turma(turma):
        return AlunoTurma.objects.filter(
            turma=turma, ativo=True,
        ).select_related('aluno__pessoa')

    @staticmethod
    def listar_por_aluno(aluno):
        return AlunoTurma.objects.filter(
            aluno=aluno, ativo=True,
        ).select_related('turma__ano_letivo')
