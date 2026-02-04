"""
academic.repositories.movimentacao_aluno_repository

Acesso a dados da entidade MovimentacaoAluno.
"""

from academic.models import MovimentacaoAluno


class MovimentacaoAlunoRepository:

    @staticmethod
    def listar_por_aluno(aluno):
        return MovimentacaoAluno.objects.filter(
            aluno=aluno,
        ).select_related('matricula').order_by('-data')
