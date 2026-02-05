"""
library.services.biblioteca_service

Regras de negocio para emprestimo e devolucao de exemplares.

Toda operacao que altere o estado de um exemplar ou emprestimo deve
passar por este service. Admin e views NUNCA devem manipular Emprestimo
ou Exemplar.situacao diretamente.
"""

from datetime import date

from django.core.exceptions import ValidationError
from django.db import transaction

from library.models import Emprestimo, Exemplar


class BibliotecaService:
    """Centraliza operacoes de emprestimo e devolucao da biblioteca."""

    @staticmethod
    @transaction.atomic
    def emprestar_exemplar(exemplar, aluno, data_emprestimo,
                           data_prevista_devolucao, turma=None, observacao=''):
        """
        Realiza o emprestimo de um exemplar a um aluno.

        Cria o registro de Emprestimo (evento) e atualiza a situacao
        do exemplar para 'emprestado'.

        Raises:
            ValidationError: se o exemplar nao esta disponivel.
            ValidationError: se o exemplar nao esta ativo.
        """
        if not exemplar.ativo:
            raise ValidationError(
                f'O exemplar {exemplar.codigo_patrimonio} nao esta ativo.'
            )

        if exemplar.situacao != Exemplar.Situacao.DISPONIVEL:
            raise ValidationError(
                f'O exemplar {exemplar.codigo_patrimonio} nao esta disponivel '
                f'(situacao atual: {exemplar.get_situacao_display()}).'
            )

        emprestimo = Emprestimo.objects.create(
            exemplar=exemplar,
            aluno=aluno,
            turma=turma,
            data_emprestimo=data_emprestimo,
            data_prevista_devolucao=data_prevista_devolucao,
            status=Emprestimo.Status.ATIVO,
            observacao=observacao,
        )

        BibliotecaService._atualizar_situacao_exemplar(exemplar)

        return emprestimo

    @staticmethod
    @transaction.atomic
    def devolver_exemplar(emprestimo, data_devolucao=None, observacao=''):
        """
        Realiza a devolucao de um emprestimo.

        Atualiza o status do emprestimo para 'devolvido', registra a
        data de devolucao e atualiza a situacao do exemplar.

        Raises:
            ValidationError: se o emprestimo nao esta ativo nem atrasado.
        """
        if emprestimo.status not in (
            Emprestimo.Status.ATIVO,
            Emprestimo.Status.ATRASADO,
        ):
            raise ValidationError(
                f'O emprestimo do exemplar {emprestimo.exemplar.codigo_patrimonio} '
                f'nao esta ativo (status atual: {emprestimo.get_status_display()}).'
            )

        emprestimo.data_devolucao = data_devolucao or date.today()
        emprestimo.status = Emprestimo.Status.DEVOLVIDO
        if observacao:
            emprestimo.observacao = (
                f'{emprestimo.observacao}\n{observacao}'.strip()
                if emprestimo.observacao else observacao
            )
        emprestimo.save(update_fields=[
            'data_devolucao', 'status', 'observacao', 'atualizado_em',
        ])

        BibliotecaService._atualizar_situacao_exemplar(emprestimo.exemplar)

    @staticmethod
    def atualizar_emprestimos_atrasados():
        """
        Atualiza emprestimos ativos com data prevista no passado para 'atrasado'.

        Pode ser chamado periodicamente (cron, celery, management command).
        """
        hoje = date.today()
        return Emprestimo.objects.filter(
            status=Emprestimo.Status.ATIVO,
            data_prevista_devolucao__lt=hoje,
        ).update(status=Emprestimo.Status.ATRASADO)

    @staticmethod
    def _atualizar_situacao_exemplar(exemplar):
        """
        Atualiza a situacao do exemplar com base nos emprestimos ativos.

        - Se tem emprestimo ativo ou atrasado -> emprestado
        - Se nao tem e esta ativo e nao esta baixado -> disponivel
        """
        tem_emprestimo_aberto = Emprestimo.objects.filter(
            exemplar=exemplar,
            status__in=[Emprestimo.Status.ATIVO, Emprestimo.Status.ATRASADO],
        ).exists()

        if tem_emprestimo_aberto:
            nova_situacao = Exemplar.Situacao.EMPRESTADO
        elif exemplar.ativo and exemplar.situacao != Exemplar.Situacao.BAIXADO:
            nova_situacao = Exemplar.Situacao.DISPONIVEL
        else:
            return

        if exemplar.situacao != nova_situacao:
            exemplar.situacao = nova_situacao
            exemplar.save(update_fields=['situacao', 'atualizado_em'])
