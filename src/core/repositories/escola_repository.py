"""
core.repositories.escola_repository

Acesso a dados da entidade Escola.
"""

from core.models import Escola


class EscolaRepository:

    @staticmethod
    def listar_ativas():
        return Escola.objects.filter(ativo=True)

    @staticmethod
    def buscar_por_cnpj(cnpj):
        return Escola.objects.filter(cnpj=cnpj).first()
