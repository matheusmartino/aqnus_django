"""
people.models.pessoa

Modelo da entidade Pessoa.
"""

from django.db import models

from core.models import ModeloBase


class Pessoa(ModeloBase):
    """
    Entidade base de pessoa física no sistema.

    Centraliza os dados pessoais para evitar duplicação.
    Aluno, Professor e Funcionário apontam para esta entidade via
    OneToOneField, permitindo que uma mesma pessoa tenha múltiplos papéis.
    """
    nome = models.CharField('nome completo', max_length=200)
    cpf = models.CharField('CPF', max_length=14, unique=True)
    data_nascimento = models.DateField('data de nascimento', null=True, blank=True)
    telefone = models.CharField('telefone', max_length=20, blank=True)
    email = models.EmailField('e-mail', blank=True)
    endereco = models.TextField('endereço', blank=True)
    ativo = models.BooleanField('ativo', default=True)

    class Meta:
        verbose_name = 'pessoa'
        verbose_name_plural = 'pessoas'
        ordering = ['nome']

    def __str__(self):
        return self.nome
