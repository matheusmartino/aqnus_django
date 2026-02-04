"""
academic.models.movimentacao_aluno

Modelo da entidade MovimentacaoAluno.
"""

from django.db import models

from core.models import ModeloBase


class MovimentacaoAluno(ModeloBase):
    """
    Registro historico de eventos na vida escolar de um aluno.

    Cada movimentacao representa um evento relevante: matricula inicial,
    transferencia, encerramento, remanejamento ou cancelamento.

    Regras:
    - Historico nunca deve ser apagado
    - Deve refletir fielmente a trajetoria do aluno na escola
    - Criado automaticamente pelo service de matricula
    """

    class TipoEvento(models.TextChoices):
        MATRICULA_INICIAL = 'matricula_inicial', 'Matricula inicial'
        TRANSFERENCIA_ENTRADA = 'transferencia_entrada', 'Transferencia (entrada)'
        TRANSFERENCIA_SAIDA = 'transferencia_saida', 'Transferencia (saida)'
        REMANEJAMENTO = 'remanejamento', 'Remanejamento'
        ENCERRAMENTO = 'encerramento', 'Encerramento'
        CANCELAMENTO = 'cancelamento', 'Cancelamento'

    aluno = models.ForeignKey(
        'people.Aluno',
        on_delete=models.PROTECT,
        related_name='movimentacoes',
        verbose_name='aluno',
    )
    tipo_evento = models.CharField(
        'tipo de evento',
        max_length=30,
        choices=TipoEvento.choices,
    )
    data = models.DateField('data')
    descricao = models.TextField('descricao')
    matricula = models.ForeignKey(
        'academic.Matricula',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='movimentacoes',
        verbose_name='matricula relacionada',
    )

    class Meta:
        verbose_name = 'movimentacao do aluno'
        verbose_name_plural = 'movimentacoes de alunos'
        ordering = ['-data', 'aluno']

    def __str__(self):
        return f'{self.aluno} — {self.get_tipo_evento_display()} ({self.data})'
