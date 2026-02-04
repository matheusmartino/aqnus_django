"""
academic.repositories.professor_disciplina_repository

Acesso a dados da entidade ProfessorDisciplina.
"""

from academic.models import ProfessorDisciplina


class ProfessorDisciplinaRepository:

    @staticmethod
    def listar_por_ano_letivo(ano_letivo):
        return ProfessorDisciplina.objects.filter(
            ano_letivo=ano_letivo,
        ).select_related('professor__pessoa', 'disciplina')

    @staticmethod
    def listar_por_professor(professor):
        return ProfessorDisciplina.objects.filter(
            professor=professor,
        ).select_related('disciplina', 'ano_letivo')
