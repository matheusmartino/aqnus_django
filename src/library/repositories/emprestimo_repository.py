"""
library.repositories.emprestimo_repository

Acesso a dados da entidade Emprestimo.
"""

from library.models import Emprestimo


class EmprestimoRepository:

    @staticmethod
    def listar_ativos():
        return Emprestimo.objects.filter(
            status__in=[Emprestimo.Status.ATIVO, Emprestimo.Status.ATRASADO],
        ).select_related('exemplar__obra', 'aluno__pessoa', 'turma')

    @staticmethod
    def listar_por_aluno(aluno):
        return Emprestimo.objects.filter(
            aluno=aluno,
        ).select_related('exemplar__obra', 'turma').order_by('-data_emprestimo')

    @staticmethod
    def listar_atrasados():
        return Emprestimo.objects.filter(
            status=Emprestimo.Status.ATRASADO,
        ).select_related('exemplar__obra', 'aluno__pessoa', 'turma')
