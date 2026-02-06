"""
academic.models.horario

Modelo da entidade Horario.
"""

from django.db import models

from core.models import ModeloBase


class Horario(ModeloBase):
    """
    Representa um horario de aula (ex: 1o horario das 07:30 as 08:20).

    Define os slots de tempo disponiveis para alocacao de aulas na grade.
    Cada escola pode ter seus proprios horarios, mas o modelo e generico.
    O campo 'ordem' define a sequencia de exibicao dos horarios.
    """

    class Turno(models.TextChoices):
        MATUTINO = 'M', 'Matutino'
        VESPERTINO = 'V', 'Vespertino'
        NOTURNO = 'N', 'Noturno'
        INTEGRAL = 'I', 'Integral'

    ordem = models.PositiveSmallIntegerField('ordem')
    hora_inicio = models.TimeField('hora de inicio')
    hora_fim = models.TimeField('hora de fim')
    turno = models.CharField(
        'turno',
        max_length=1,
        choices=Turno.choices,
        default=Turno.MATUTINO,
    )

    class Meta:
        verbose_name = 'horario'
        verbose_name_plural = 'horarios'
        ordering = ['turno', 'ordem']
        constraints = [
            models.UniqueConstraint(
                fields=['turno', 'ordem'],
                name='unique_turno_ordem',
            ),
        ]

    def __str__(self):
        return f'{self.ordem}o horario ({self.hora_inicio.strftime("%H:%M")} - {self.hora_fim.strftime("%H:%M")}) — {self.get_turno_display()}'
