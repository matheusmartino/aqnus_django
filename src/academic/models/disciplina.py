"""
academic.models.disciplina

Modelo da entidade Disciplina.
"""

from django.db import models

from core.models import ModeloBase


class Disciplina(ModeloBase):
    """
    Representa uma disciplina / componente curricular (ex: Matematica, Portugues).

    E uma entidade independente de ano letivo — a mesma disciplina pode ser
    oferecida em varios anos. O vinculo com professores e feito via
    ProfessorDisciplina.
    """
    nome = models.CharField('nome', max_length=200)
    codigo = models.CharField('codigo', max_length=20, unique=True)
    carga_horaria = models.PositiveIntegerField('carga horaria (h/ano)')
    ativa = models.BooleanField('ativa', default=True)

    class Meta:
        verbose_name = 'disciplina'
        verbose_name_plural = 'disciplinas'
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} ({self.codigo})'
