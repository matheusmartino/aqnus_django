"""
people.models.responsavel

Modelo da entidade Responsavel.
"""

from django.db import models

from core.models import ModeloBase
from .pessoa import Pessoa


class Responsavel(ModeloBase):
    """
    Perfil de responsavel / filiacao.

    Vinculado a uma Pessoa via OneToOneField (mesmo padrao de Aluno,
    Professor e Funcionario). Representa alguem que pode ser pai, mae
    ou responsavel legal de um ou mais alunos.

    O vinculo especifico com cada aluno e feito via AlunoResponsavel,
    permitindo que irmaos compartilhem os mesmos responsaveis sem
    duplicar dados pessoais.
    """

    class Tipo(models.TextChoices):
        PAI = 'pai', 'Pai'
        MAE = 'mae', 'Mae'
        RESPONSAVEL_LEGAL = 'responsavel_legal', 'Responsavel legal'

    pessoa = models.OneToOneField(
        Pessoa,
        on_delete=models.CASCADE,
        related_name='responsavel',
        verbose_name='pessoa',
    )
    tipo = models.CharField(
        'tipo',
        max_length=20,
        choices=Tipo.choices,
    )
    ativo = models.BooleanField('ativo', default=True)

    class Meta:
        verbose_name = 'responsavel'
        verbose_name_plural = 'responsaveis'
        ordering = ['pessoa__nome']

    def __str__(self):
        return f'{self.pessoa.nome} ({self.get_tipo_display()})'
