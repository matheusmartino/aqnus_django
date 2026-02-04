"""
academic.models.aluno_turma

Modelo da entidade AlunoTurma.
"""

from django.db import models

from core.models import ModeloBase


class AlunoTurma(ModeloBase):
    """
    Matricula de um aluno em uma turma.

    Registra o vinculo entre aluno e turma com data de matricula e status.
    A unicidade e por (aluno, turma) — um aluno nao pode estar matriculado
    duas vezes na mesma turma.
    """
    aluno = models.ForeignKey(
        'people.Aluno',
        on_delete=models.PROTECT,
        related_name='turmas_matriculadas',
        verbose_name='aluno',
    )
    turma = models.ForeignKey(
        'academic.Turma',
        on_delete=models.PROTECT,
        related_name='alunos_matriculados',
        verbose_name='turma',
    )
    data_matricula = models.DateField('data de matricula')
    ativo = models.BooleanField('ativo', default=True)

    class Meta:
        verbose_name = 'aluno-turma'
        verbose_name_plural = 'alunos-turmas'
        ordering = ['turma', 'aluno']
        constraints = [
            models.UniqueConstraint(
                fields=['aluno', 'turma'],
                name='unique_aluno_turma',
            ),
        ]

    def __str__(self):
        return f'{self.aluno} — {self.turma}'
