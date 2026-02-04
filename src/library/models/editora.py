"""
library.models.editora

Modelo da entidade Editora.
"""

from django.db import models

from core.models import ModeloBase


class Editora(ModeloBase):
    """
    Editora responsavel pela publicacao de obras do acervo.

    Representa a casa editorial vinculada a uma ou mais obras.
    """

    nome = models.CharField('nome', max_length=200)
    ativo = models.BooleanField('ativo', default=True)

    class Meta:
        verbose_name = 'editora'
        verbose_name_plural = 'editoras'
        ordering = ['nome']

    def __str__(self):
        return self.nome
