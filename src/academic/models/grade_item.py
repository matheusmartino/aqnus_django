"""
academic.models.grade_item

Modelo da entidade GradeItem.
"""

from django.db import models

from core.models import ModeloBase


class DiaSemana(models.TextChoices):
    """
    Dias da semana para alocacao de aulas.

    Definido como TextChoices para uso em GradeItem e outras entidades
    que necessitem referenciar dias da semana.
    """
    SEGUNDA = 'SEG', 'Segunda-feira'
    TERCA = 'TER', 'Terca-feira'
    QUARTA = 'QUA', 'Quarta-feira'
    QUINTA = 'QUI', 'Quinta-feira'
    SEXTA = 'SEX', 'Sexta-feira'
    SABADO = 'SAB', 'Sabado'


class GradeItem(ModeloBase):
    """
    Representa uma aula na grade horaria (ex: Matematica na segunda, 1o horario).

    Vincula uma disciplina e professor a um slot especifico (dia + horario)
    dentro de uma grade horaria.

    As regras de conflito sao:
    - Um professor nao pode ter duas aulas no mesmo dia/horario
    - Uma turma nao pode ter duas aulas no mesmo dia/horario
    - O professor deve estar habilitado para lecionar a disciplina

    Essas validacoes sao feitas pelo GradeService, nao pelo model.
    """
    grade_horaria = models.ForeignKey(
        'academic.GradeHoraria',
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='grade horaria',
    )
    dia_semana = models.CharField(
        'dia da semana',
        max_length=3,
        choices=DiaSemana.choices,
    )
    horario = models.ForeignKey(
        'academic.Horario',
        on_delete=models.PROTECT,
        related_name='grade_itens',
        verbose_name='horario',
    )
    disciplina = models.ForeignKey(
        'academic.Disciplina',
        on_delete=models.PROTECT,
        related_name='grade_itens',
        verbose_name='disciplina',
    )
    professor = models.ForeignKey(
        'people.Professor',
        on_delete=models.PROTECT,
        related_name='grade_itens',
        verbose_name='professor',
    )

    class Meta:
        verbose_name = 'item da grade'
        verbose_name_plural = 'itens da grade'
        ordering = ['grade_horaria', 'dia_semana', 'horario__ordem']
        constraints = [
            models.UniqueConstraint(
                fields=['grade_horaria', 'dia_semana', 'horario'],
                name='unique_grade_dia_horario',
            ),
        ]

    def __str__(self):
        return f'{self.get_dia_semana_display()} {self.horario.ordem}o h — {self.disciplina} ({self.professor})'
