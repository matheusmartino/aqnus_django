"""
core.models.escola

Modelo da entidade Escola.
"""

from django.db import models

from .base import ModeloBase


class Escola(ModeloBase):
    """
    Representa uma unidade escolar / instituição de ensino.

    Cada escola possui identificação própria (CNPJ), endereço e status de atividade.
    Serve como entidade raiz para vincular turmas, matrículas e demais dados
    acadêmicos nas etapas futuras.
    """
    nome = models.CharField('nome', max_length=200)
    cnpj = models.CharField('CNPJ', max_length=18, unique=True)
    endereco = models.TextField('endereço', blank=True)
    telefone = models.CharField('telefone', max_length=20, blank=True)
    email = models.EmailField('e-mail', blank=True)
    ativo = models.BooleanField('ativo', default=True)

    class Meta:
        verbose_name = 'escola'
        verbose_name_plural = 'escolas'
        ordering = ['nome']

    def __str__(self):
        return self.nome
