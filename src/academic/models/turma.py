"""
academic.models.turma

Modelo da entidade Turma.
"""

from django.db import models

from core.models import ModeloBase


class Turma(ModeloBase):
    """
    Representa uma turma dentro de um ano letivo e escola (ex: 5o Ano A - 2025).

    Agrupa alunos para fins de organizacao academica. O vinculo de alunos
    a turma e feito via AlunoTurma.
    """
    nome = models.CharField('nome', max_length=100)
    ano_letivo = models.ForeignKey(
        'academic.AnoLetivo',
        on_delete=models.PROTECT,
        related_name='turmas',
        verbose_name='ano letivo',
    )
    escola = models.ForeignKey(
        'core.Escola',
        on_delete=models.PROTECT,
        related_name='turmas',
        verbose_name='escola',
    )
    ativa = models.BooleanField('ativa', default=True)

    class Meta:
        verbose_name = 'turma'
        verbose_name_plural = 'turmas'
        ordering = ['ano_letivo', 'nome']
        constraints = [
            models.UniqueConstraint(
                fields=['nome', 'ano_letivo', 'escola'],
                name='unique_turma_ano_escola',
            ),
        ]

    def __str__(self):
        return f'{self.nome} — {self.ano_letivo}'
