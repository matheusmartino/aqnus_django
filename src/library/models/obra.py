"""
library.models.obra

Modelo da entidade Obra.
"""

from django.db import models

from core.models import ModeloBase


class Obra(ModeloBase):
    """
    Obra do acervo da biblioteca (livro, periodico, publicacao).

    Representa o CONTEUDO — o titulo intelectual. Uma obra pode ter
    multiplos exemplares fisicos (modelo Exemplar). Diferente de Exemplar,
    a Obra nao e emprestada diretamente — o emprestimo e feito sobre o
    exemplar fisico.
    """

    titulo = models.CharField('titulo', max_length=300)
    autores = models.ManyToManyField(
        'library.Autor',
        blank=True,
        related_name='obras',
        verbose_name='autores',
    )
    editora = models.ForeignKey(
        'library.Editora',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='obras',
        verbose_name='editora',
    )
    assunto = models.ForeignKey(
        'library.Assunto',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='obras',
        verbose_name='assunto',
    )
    isbn = models.CharField(
        'ISBN',
        max_length=20,
        blank=True,
    )
    ano_publicacao = models.PositiveIntegerField(
        'ano de publicacao',
        null=True,
        blank=True,
    )
    observacao = models.TextField('observacao', blank=True)
    ativa = models.BooleanField('ativa', default=True)

    class Meta:
        verbose_name = 'obra'
        verbose_name_plural = 'obras'
        ordering = ['titulo']
        constraints = [
            models.UniqueConstraint(
                fields=['isbn'],
                condition=~models.Q(isbn=''),
                name='unique_isbn_quando_preenchido',
            ),
        ]

    def __str__(self):
        return self.titulo
