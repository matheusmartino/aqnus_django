"""
accounts.repositories.usuario_repository

Acesso a dados da entidade Usuario.
"""

from accounts.models import Usuario


class UsuarioRepository:

    @staticmethod
    def listar_por_papel(papel):
        return Usuario.objects.filter(papel=papel, is_active=True)

    @staticmethod
    def buscar_por_username(username):
        return Usuario.objects.filter(username=username).first()
