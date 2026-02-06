"""
academic.models.grade_horaria

Modelo da entidade GradeHoraria.
"""

from django.db import models

from core.models import ModeloBase


class GradeHoraria(ModeloBase):
    """
    Representa a grade horaria de uma turma em um ano letivo.

    A grade horaria organiza as aulas semanais da turma, vinculando
    disciplinas e professores a dias e horarios especificos.

    Cada turma pode ter apenas uma grade ativa por vez. Grades inativas
    podem ser mantidas para referencia, mas nao representam o horario
    vigente.

    A grade NAO e historica — ela representa o estado atual do horario.
    Se a turma mudar de horario, a grade e editada, nao versionada.
    Isso simplifica a operacao e evita complexidade desnecessaria.
    """
    turma = models.ForeignKey(
        'academic.Turma',
        on_delete=models.PROTECT,
        related_name='grades_horarias',
        verbose_name='turma',
    )
    ano_letivo = models.ForeignKey(
        'academic.AnoLetivo',
        on_delete=models.PROTECT,
        related_name='grades_horarias',
        verbose_name='ano letivo',
    )
    ativa = models.BooleanField('ativa', default=True)
    observacao = models.TextField('observacao', blank=True, default='')

    class Meta:
        verbose_name = 'grade horaria'
        verbose_name_plural = 'grades horarias'
        ordering = ['ano_letivo', 'turma']
        constraints = [
            models.UniqueConstraint(
                fields=['turma', 'ano_letivo'],
                condition=models.Q(ativa=True),
                name='unique_grade_ativa_turma_ano',
            ),
        ]

    def __str__(self):
        status = 'Ativa' if self.ativa else 'Inativa'
        return f'Grade {self.turma} — {self.ano_letivo} ({status})'
