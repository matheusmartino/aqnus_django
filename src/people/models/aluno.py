"""
people.models.aluno

Modelo da entidade Aluno.
"""

from django.db import models

from core.models import ModeloBase
from .pessoa import Pessoa


class Aluno(ModeloBase):
    """
    Perfil acadêmico de um aluno.

    Vinculado a uma Pessoa. Contém dados específicos da vida escolar:
    matrícula, data de ingresso e situação atual.
    """

    class Situacao(models.TextChoices):
        ATIVO = 'ativo', 'Ativo'
        INATIVO = 'inativo', 'Inativo'
        TRANSFERIDO = 'transferido', 'Transferido'
        FORMADO = 'formado', 'Formado'
        DESISTENTE = 'desistente', 'Desistente'

    pessoa = models.OneToOneField(
        Pessoa,
        on_delete=models.CASCADE,
        related_name='aluno',
        verbose_name='pessoa',
    )
    matricula = models.CharField('matrícula', max_length=30, unique=True)
    data_ingresso = models.DateField('data de ingresso')
    situacao = models.CharField(
        'situação',
        max_length=20,
        choices=Situacao.choices,
        default=Situacao.ATIVO,
    )

    class Meta:
        verbose_name = 'aluno'
        verbose_name_plural = 'alunos'
        ordering = ['pessoa__nome']

    def __str__(self):
        return f'{self.pessoa.nome} ({self.matricula})'
