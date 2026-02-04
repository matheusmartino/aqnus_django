"""
people.models.professor

Modelo da entidade Professor.
"""

from django.db import models

from core.models import ModeloBase
from .pessoa import Pessoa


class Professor(ModeloBase):
    """
    Perfil docente de um professor.

    Vinculado a uma Pessoa. Contém formação acadêmica e carga horária
    máxima permitida.
    """
    pessoa = models.OneToOneField(
        Pessoa,
        on_delete=models.CASCADE,
        related_name='professor',
        verbose_name='pessoa',
    )
    formacao = models.CharField('formação', max_length=200)
    carga_horaria_max = models.PositiveIntegerField(
        'carga horária máxima (h/semana)',
        default=40,
    )
    ativo = models.BooleanField('ativo', default=True)

    class Meta:
        verbose_name = 'professor'
        verbose_name_plural = 'professores'
        ordering = ['pessoa__nome']

    def __str__(self):
        return self.pessoa.nome
