"""
library.models.exemplar

Modelo da entidade Exemplar.
"""

from django.db import models

from core.models import ModeloBase


class Exemplar(ModeloBase):
    """
    Exemplar fisico de uma obra do acervo.

    Representa o OBJETO — a copia fisica de uma obra. Cada exemplar tem
    um codigo de patrimonio unico e controle de estado fisico e situacao.

    A situacao (disponivel/emprestado/indisponivel/baixado) e atualizada
    SOMENTE pelo BibliotecaService, nunca manualmente pelo admin.
    """

    class EstadoFisico(models.TextChoices):
        BOM = 'bom', 'Bom'
        REGULAR = 'regular', 'Regular'
        RUIM = 'ruim', 'Ruim'
        DANIFICADO = 'danificado', 'Danificado'

    class Situacao(models.TextChoices):
        DISPONIVEL = 'disponivel', 'Disponivel'
        EMPRESTADO = 'emprestado', 'Emprestado'
        INDISPONIVEL = 'indisponivel', 'Indisponivel'
        BAIXADO = 'baixado', 'Baixado'

    obra = models.ForeignKey(
        'library.Obra',
        on_delete=models.PROTECT,
        related_name='exemplares',
        verbose_name='obra',
    )
    codigo_patrimonio = models.CharField(
        'codigo de patrimonio',
        max_length=50,
        unique=True,
    )
    estado_fisico = models.CharField(
        'estado fisico',
        max_length=20,
        choices=EstadoFisico.choices,
        default=EstadoFisico.BOM,
    )
    situacao = models.CharField(
        'situacao',
        max_length=20,
        choices=Situacao.choices,
        default=Situacao.DISPONIVEL,
    )
    ativo = models.BooleanField('ativo', default=True)

    class Meta:
        verbose_name = 'exemplar'
        verbose_name_plural = 'exemplares'
        ordering = ['codigo_patrimonio']

    def __str__(self):
        return f'{self.codigo_patrimonio} — {self.obra.titulo}'
