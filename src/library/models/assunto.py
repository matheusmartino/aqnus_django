"""
library.models.assunto

Modelo da entidade Assunto.
"""

from django.db import models

from core.models import ModeloBase


class Assunto(ModeloBase):
    """
    Assunto ou categoria tematica de uma obra do acervo.

    Permite classificar obras por tema (ex: Literatura, Ciencias, Historia).
    Cada assunto e unico no sistema.
    """

    nome = models.CharField('nome', max_length=200, unique=True)
    ativo = models.BooleanField('ativo', default=True)

    class Meta:
        verbose_name = 'assunto'
        verbose_name_plural = 'assuntos'
        ordering = ['nome']

    def __str__(self):
        return self.nome
