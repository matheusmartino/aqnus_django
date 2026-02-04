"""
academic.models.matricula

Modelo da entidade Matricula.
"""

from django.db import models

from core.models import ModeloBase


class Matricula(ModeloBase):
    """
    Ato administrativo de matricula de um aluno.

    Representa o EVENTO da matricula (historico), nao o estado atual.
    O estado atual do aluno numa turma e representado por AlunoTurma.

    Regras:
    - Um aluno so pode ter UMA matricula ativa por ano letivo
      (enforced via UniqueConstraint parcial + service)
    - Matricula e historico — nao deve ser apagada
    - Tipos: inicial (primeiro ingresso), transferencia (vinda de outra
      turma/escola), remanejamento (movimentacao interna)
    - Status: ativa, encerrada, cancelada
    """

    class Tipo(models.TextChoices):
        INICIAL = 'inicial', 'Inicial'
        TRANSFERENCIA = 'transferencia', 'Transferencia'
        REMANEJAMENTO = 'remanejamento', 'Remanejamento'

    class Status(models.TextChoices):
        ATIVA = 'ativa', 'Ativa'
        ENCERRADA = 'encerrada', 'Encerrada'
        CANCELADA = 'cancelada', 'Cancelada'

    aluno = models.ForeignKey(
        'people.Aluno',
        on_delete=models.PROTECT,
        related_name='matriculas',
        verbose_name='aluno',
    )
    turma = models.ForeignKey(
        'academic.Turma',
        on_delete=models.PROTECT,
        related_name='matriculas',
        verbose_name='turma',
    )
    ano_letivo = models.ForeignKey(
        'academic.AnoLetivo',
        on_delete=models.PROTECT,
        related_name='matriculas',
        verbose_name='ano letivo',
    )
    data_matricula = models.DateField('data da matricula')
    tipo = models.CharField(
        'tipo',
        max_length=20,
        choices=Tipo.choices,
        default=Tipo.INICIAL,
    )
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.ATIVA,
    )
    observacao = models.TextField('observacao', blank=True)

    class Meta:
        verbose_name = 'matricula'
        verbose_name_plural = 'matriculas'
        ordering = ['-data_matricula', 'aluno']
        constraints = [
            models.UniqueConstraint(
                fields=['aluno', 'ano_letivo'],
                condition=models.Q(status='ativa'),
                name='unique_matricula_ativa_por_ano',
            ),
        ]

    def __str__(self):
        return f'{self.aluno} — {self.turma} ({self.get_status_display()})'
