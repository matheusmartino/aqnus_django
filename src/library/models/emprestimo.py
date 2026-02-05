"""
library.models.emprestimo

Modelo da entidade Emprestimo.
"""

from django.db import models

from core.models import ModeloBase


class Emprestimo(ModeloBase):
    """
    Emprestimo de um exemplar da biblioteca.

    Representa o EVENTO de emprestimo — quando um exemplar e emprestado
    a um aluno. O status (ativo/devolvido/atrasado) e controlado pelo
    BibliotecaService.

    Constraint parcial garante que cada exemplar so pode ter um
    emprestimo ativo por vez.
    """

    class Status(models.TextChoices):
        ATIVO = 'ativo', 'Ativo'
        DEVOLVIDO = 'devolvido', 'Devolvido'
        ATRASADO = 'atrasado', 'Atrasado'

    exemplar = models.ForeignKey(
        'library.Exemplar',
        on_delete=models.PROTECT,
        related_name='emprestimos',
        verbose_name='exemplar',
    )
    aluno = models.ForeignKey(
        'people.Aluno',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='emprestimos',
        verbose_name='aluno',
    )
    turma = models.ForeignKey(
        'academic.Turma',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='emprestimos',
        verbose_name='turma',
    )
    data_emprestimo = models.DateField('data do emprestimo')
    data_prevista_devolucao = models.DateField('data prevista de devolucao')
    data_devolucao = models.DateField(
        'data de devolucao',
        null=True,
        blank=True,
    )
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.ATIVO,
    )
    observacao = models.TextField('observacao', blank=True)

    class Meta:
        verbose_name = 'emprestimo'
        verbose_name_plural = 'emprestimos'
        ordering = ['-data_emprestimo']
        constraints = [
            models.UniqueConstraint(
                fields=['exemplar'],
                condition=models.Q(status='ativo') | models.Q(status='atrasado'),
                name='unique_emprestimo_ativo_por_exemplar',
            ),
        ]

    def __str__(self):
        aluno_nome = self.aluno if self.aluno else 'Sem aluno'
        return (
            f'{self.exemplar.codigo_patrimonio} — {aluno_nome} '
            f'({self.get_status_display()})'
        )
