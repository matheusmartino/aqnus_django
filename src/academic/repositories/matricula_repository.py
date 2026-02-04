"""
academic.repositories.matricula_repository

Acesso a dados da entidade Matricula.
"""

from academic.models import Matricula


class MatriculaRepository:

    @staticmethod
    def listar_por_aluno(aluno):
        return Matricula.objects.filter(
            aluno=aluno,
        ).select_related('turma', 'ano_letivo').order_by('-data_matricula')

    @staticmethod
    def buscar_ativa_por_aluno_e_ano(aluno, ano_letivo):
        return Matricula.objects.filter(
            aluno=aluno,
            ano_letivo=ano_letivo,
            status='ativa',
        ).select_related('turma').first()

    @staticmethod
    def listar_por_turma(turma):
        return Matricula.objects.filter(
            turma=turma,
            status='ativa',
        ).select_related('aluno__pessoa')
