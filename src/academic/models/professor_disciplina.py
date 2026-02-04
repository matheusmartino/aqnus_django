"""
academic.models.professor_disciplina

Modelo da entidade ProfessorDisciplina.
"""

from django.db import models

from core.models import ModeloBase


class ProfessorDisciplina(ModeloBase):
    """
    Vincula um professor a uma disciplina em um ano letivo especifico.

    Um mesmo professor pode lecionar varias disciplinas, e uma mesma
    disciplina pode ser lecionada por varios professores (em turmas
    diferentes). A unicidade e por (professor, disciplina, ano_letivo).
    """
    professor = models.ForeignKey(
        'people.Professor',
        on_delete=models.PROTECT,
        related_name='disciplinas_lecionadas',
        verbose_name='professor',
    )
    disciplina = models.ForeignKey(
        'academic.Disciplina',
        on_delete=models.PROTECT,
        related_name='professores_vinculados',
        verbose_name='disciplina',
    )
    ano_letivo = models.ForeignKey(
        'academic.AnoLetivo',
        on_delete=models.PROTECT,
        related_name='professor_disciplinas',
        verbose_name='ano letivo',
    )

    class Meta:
        verbose_name = 'professor-disciplina'
        verbose_name_plural = 'professores-disciplinas'
        ordering = ['ano_letivo', 'professor', 'disciplina']
        constraints = [
            models.UniqueConstraint(
                fields=['professor', 'disciplina', 'ano_letivo'],
                name='unique_prof_disc_ano',
            ),
        ]

    def __str__(self):
        return f'{self.professor} — {self.disciplina} ({self.ano_letivo})'
