"""
people.models.aluno_responsavel

Modelo da entidade AlunoResponsavel.
"""

from django.db import models

from core.models import ModeloBase


class AlunoResponsavel(ModeloBase):
    """
    Vinculo entre um aluno e um responsavel.

    Modela a filiacao como relacionamento, nao como atributo do aluno.
    Permite que irmaos compartilhem os mesmos responsaveis e que um
    aluno tenha multiplos responsaveis (pai, mae, tutor).

    A unicidade e por (aluno, responsavel) — um responsavel nao pode
    estar vinculado duas vezes ao mesmo aluno.
    """

    class TipoVinculo(models.TextChoices):
        PAI = 'pai', 'Pai'
        MAE = 'mae', 'Mae'
        TUTOR = 'tutor', 'Tutor'

    aluno = models.ForeignKey(
        'people.Aluno',
        on_delete=models.PROTECT,
        related_name='responsaveis',
        verbose_name='aluno',
    )
    responsavel = models.ForeignKey(
        'people.Responsavel',
        on_delete=models.PROTECT,
        related_name='alunos',
        verbose_name='responsavel',
    )
    tipo_vinculo = models.CharField(
        'tipo de vinculo',
        max_length=20,
        choices=TipoVinculo.choices,
    )
    responsavel_principal = models.BooleanField(
        'responsavel principal',
        default=False,
    )
    autorizado_retirar_aluno = models.BooleanField(
        'autorizado a retirar o aluno',
        default=True,
    )

    class Meta:
        verbose_name = 'aluno-responsavel'
        verbose_name_plural = 'alunos-responsaveis'
        ordering = ['aluno', 'responsavel']
        constraints = [
            models.UniqueConstraint(
                fields=['aluno', 'responsavel'],
                name='unique_aluno_responsavel',
            ),
        ]

    def __str__(self):
        return f'{self.aluno} — {self.responsavel}'
