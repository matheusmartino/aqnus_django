"""
library.models.autor

Modelo da entidade Autor.
"""

from django.db import models

from core.models import ModeloBase


class Autor(ModeloBase):
    """
    Autor de uma obra do acervo da biblioteca.

    Representa a pessoa responsavel pela autoria de um livro ou publicacao.
    Um autor pode estar vinculado a multiplas obras.
    """

    nome = models.CharField('nome', max_length=200)
    ativo = models.BooleanField('ativo', default=True)

    class Meta:
        verbose_name = 'autor'
        verbose_name_plural = 'autores'
        ordering = ['nome']

    def __str__(self):
        return self.nome
