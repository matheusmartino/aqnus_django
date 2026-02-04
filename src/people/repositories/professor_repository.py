"""
people.repositories.professor_repository

Acesso a dados da entidade Professor.
"""

from people.models import Professor


class ProfessorRepository:

    @staticmethod
    def listar_ativos():
        return Professor.objects.filter(ativo=True).select_related('pessoa')
