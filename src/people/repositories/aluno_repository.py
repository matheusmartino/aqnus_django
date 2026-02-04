"""
people.repositories.aluno_repository

Acesso a dados da entidade Aluno.
"""

from people.models import Aluno


class AlunoRepository:

    @staticmethod
    def listar_ativos():
        return Aluno.objects.filter(situacao='ativo').select_related('pessoa')

    @staticmethod
    def buscar_por_matricula(matricula):
        return Aluno.objects.filter(matricula=matricula).select_related('pessoa').first()
