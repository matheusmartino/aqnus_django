"""
people.repositories.funcionario_repository

Acesso a dados da entidade Funcionário.
"""

from people.models import Funcionario


class FuncionarioRepository:

    @staticmethod
    def listar_ativos():
        return Funcionario.objects.filter(ativo=True).select_related('pessoa')

    @staticmethod
    def listar_por_setor(setor):
        return Funcionario.objects.filter(setor=setor, ativo=True).select_related('pessoa')
