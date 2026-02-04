"""
library.repositories.obra_repository

Acesso a dados da entidade Obra.
"""

from library.models import Obra


class ObraRepository:

    @staticmethod
    def listar_ativas():
        return Obra.objects.filter(
            ativa=True,
        ).select_related('editora', 'assunto').prefetch_related('autores')

    @staticmethod
    def listar_por_assunto(assunto):
        return Obra.objects.filter(
            assunto=assunto,
            ativa=True,
        ).select_related('editora').prefetch_related('autores')

    @staticmethod
    def listar_por_autor(autor):
        return Obra.objects.filter(
            autores=autor,
            ativa=True,
        ).select_related('editora', 'assunto')

    @staticmethod
    def buscar_por_isbn(isbn):
        return Obra.objects.filter(
            isbn=isbn,
        ).select_related('editora', 'assunto').first()
