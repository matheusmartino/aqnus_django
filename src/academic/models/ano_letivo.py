"""
academic.models.ano_letivo

Modelo da entidade AnoLetivo.
"""

from django.db import models

from core.models import ModeloBase


class AnoLetivo(ModeloBase):
    """
    Representa um ano letivo (ex: 2025).

    Define o periodo de vigencia das turmas, vinculos de professores
    a disciplinas e matriculas de alunos. Apenas um ano letivo deve
    estar ativo por vez na operacao normal da escola.
    """
    nome = models.CharField('nome', max_length=20, unique=True)
    data_inicio = models.DateField('data de inicio')
    data_fim = models.DateField('data de fim')
    ativo = models.BooleanField('ativo', default=True)

    class Meta:
        verbose_name = 'ano letivo'
        verbose_name_plural = 'anos letivos'
        ordering = ['-nome']

    def __str__(self):
        return self.nome
