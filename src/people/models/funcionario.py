"""
people.models.funcionario

Modelo da entidade Funcionário.
"""

from django.db import models

from core.models import ModeloBase
from .pessoa import Pessoa


class Funcionario(ModeloBase):
    """
    Perfil de colaborador / funcionário.

    Vinculado a uma Pessoa. Contém cargo, setor e status de atividade.
    """
    pessoa = models.OneToOneField(
        Pessoa,
        on_delete=models.CASCADE,
        related_name='funcionario',
        verbose_name='pessoa',
    )
    cargo = models.CharField('cargo', max_length=100)
    setor = models.CharField('setor', max_length=100, blank=True)
    ativo = models.BooleanField('ativo', default=True)

    class Meta:
        verbose_name = 'funcionário'
        verbose_name_plural = 'funcionários'
        ordering = ['pessoa__nome']

    def __str__(self):
        return f'{self.pessoa.nome} - {self.cargo}'
