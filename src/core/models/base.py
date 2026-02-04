"""
core.models.base

Modelo abstrato base do sistema AQNUS.
"""

from django.db import models


class ModeloBase(models.Model):
    """
    Modelo abstrato que fornece campos de auditoria para todos os models do sistema.

    Campos:
        criado_em: data/hora de criação do registro (preenchido automaticamente)
        atualizado_em: data/hora da última atualização (atualizado automaticamente)
    """
    criado_em = models.DateTimeField('criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        abstract = True
