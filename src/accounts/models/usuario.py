"""
accounts.models.usuario

Modelo doUsuário customizado do sistema AQNUS.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Usuário do sistema AQNUS.

    Estende o usuário padrão do Django para permitir:
    - Vínculo com a entidade Pessoa (aluno, professor, funcionário)
    - Identificação do papel principal do usuário no sistema

    O vínculo com Pessoa é opcional: nem todo usuário do sistema precisa
    ser uma pessoa cadastrada (ex: admin técnico).
    """

    class Papel(models.TextChoices):
        ADMINISTRADOR = 'admin', 'Administrador'
        SECRETARIA = 'secretaria', 'Secretaria'
        PROFESSOR = 'professor', 'Professor'
        BIBLIOTECA = 'biblioteca', 'Biblioteca'

    pessoa = models.OneToOneField(
        'people.Pessoa',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuario',
        verbose_name='pessoa vinculada',
    )

    papel = models.CharField(
        'papel no sistema',
        max_length=20,
        choices=Papel.choices,
        default=Papel.SECRETARIA,
    )

    class Meta:
        verbose_name = 'usuário'
        verbose_name_plural = 'usuários'

    def __str__(self):
        return self.get_full_name() or self.username
