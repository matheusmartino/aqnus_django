"""
academic.repositories.disciplina_repository

Acesso a dados da entidade Disciplina.
"""

from academic.models import Disciplina


class DisciplinaRepository:

    @staticmethod
    def listar_ativas():
        return Disciplina.objects.filter(ativa=True)

    @staticmethod
    def buscar_por_codigo(codigo):
        return Disciplina.objects.filter(codigo=codigo).first()
