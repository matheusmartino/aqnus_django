"""
people.repositories.pessoa_repository

Acesso a dados da entidade Pessoa.
"""

from people.models import Pessoa


class PessoaRepository:

    @staticmethod
    def listar_ativas():
        return Pessoa.objects.filter(ativo=True)

    @staticmethod
    def buscar_por_cpf(cpf):
        return Pessoa.objects.filter(cpf=cpf).first()
