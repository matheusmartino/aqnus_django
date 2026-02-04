"""
academic.services.matricula_service

Regras de negocio para matricula, transferencia e encerramento de alunos.

Toda operacao que altere o estado do aluno (matricula, transferencia,
encerramento) deve passar por este service. Admin e views NUNCA devem
manipular Matricula, AlunoTurma e MovimentacaoAluno diretamente.
"""

from django.core.exceptions import ValidationError
from django.db import transaction

from academic.models import AlunoTurma, Matricula, MovimentacaoAluno


class MatriculaService:
    """Centraliza operacoes de matricula escolar."""

    @staticmethod
    @transaction.atomic
    def matricular_aluno(aluno, turma, ano_letivo, data_matricula,
                         tipo=Matricula.Tipo.INICIAL, observacao=''):
        """
        Realiza a matricula de um aluno em uma turma.

        Cria o registro de Matricula (evento/historico), atualiza o
        AlunoTurma (estado atual) e registra a movimentacao.

        Raises:
            ValidationError: se o aluno ja possui matricula ativa no ano letivo.
        """
        # Valida: aluno nao pode ter matricula ativa no mesmo ano
        matricula_existente = Matricula.objects.filter(
            aluno=aluno,
            ano_letivo=ano_letivo,
            status=Matricula.Status.ATIVA,
        ).first()

        if matricula_existente:
            raise ValidationError(
                f'O aluno {aluno} ja possui matricula ativa no ano letivo '
                f'{ano_letivo} (turma: {matricula_existente.turma}).'
            )

        # Cria a matricula (historico)
        matricula = Matricula.objects.create(
            aluno=aluno,
            turma=turma,
            ano_letivo=ano_letivo,
            data_matricula=data_matricula,
            tipo=tipo,
            status=Matricula.Status.ATIVA,
            observacao=observacao,
        )

        # Cria/atualiza o estado atual (AlunoTurma)
        AlunoTurma.objects.update_or_create(
            aluno=aluno,
            turma=turma,
            defaults={
                'data_matricula': data_matricula,
                'ativo': True,
            },
        )

        # Registra movimentacao
        tipo_evento_map = {
            Matricula.Tipo.INICIAL: MovimentacaoAluno.TipoEvento.MATRICULA_INICIAL,
            Matricula.Tipo.TRANSFERENCIA: MovimentacaoAluno.TipoEvento.TRANSFERENCIA_ENTRADA,
            Matricula.Tipo.REMANEJAMENTO: MovimentacaoAluno.TipoEvento.REMANEJAMENTO,
        }

        MovimentacaoAluno.objects.create(
            aluno=aluno,
            tipo_evento=tipo_evento_map.get(
                tipo, MovimentacaoAluno.TipoEvento.MATRICULA_INICIAL
            ),
            data=data_matricula,
            descricao=(
                f'Matricula {tipo} na turma {turma} — {ano_letivo}.'
                f'{" " + observacao if observacao else ""}'
            ),
            matricula=matricula,
        )

        return matricula

    @staticmethod
    @transaction.atomic
    def encerrar_matricula(matricula, data, motivo=''):
        """
        Encerra uma matricula ativa.

        Atualiza o status da matricula para 'encerrada', desativa o
        AlunoTurma correspondente e registra a movimentacao.

        Raises:
            ValidationError: se a matricula nao esta ativa.
        """
        if matricula.status != Matricula.Status.ATIVA:
            raise ValidationError(
                f'A matricula do aluno {matricula.aluno} nao esta ativa '
                f'(status atual: {matricula.get_status_display()}).'
            )

        # Encerra a matricula
        matricula.status = Matricula.Status.ENCERRADA
        matricula.save(update_fields=['status', 'atualizado_em'])

        # Desativa o AlunoTurma
        AlunoTurma.objects.filter(
            aluno=matricula.aluno,
            turma=matricula.turma,
        ).update(ativo=False)

        # Registra movimentacao
        MovimentacaoAluno.objects.create(
            aluno=matricula.aluno,
            tipo_evento=MovimentacaoAluno.TipoEvento.ENCERRAMENTO,
            data=data,
            descricao=(
                f'Encerramento da matricula na turma {matricula.turma} '
                f'— {matricula.ano_letivo}.'
                f'{" Motivo: " + motivo if motivo else ""}'
            ),
            matricula=matricula,
        )

    @staticmethod
    @transaction.atomic
    def transferir_aluno(matricula_atual, nova_turma, data, observacao=''):
        """
        Transfere um aluno de uma turma para outra.

        Encerra a matricula atual, cria uma nova matricula do tipo
        'transferencia' na nova turma, atualiza AlunoTurma e registra
        ambas as movimentacoes (saida e entrada).

        Raises:
            ValidationError: se a matricula nao esta ativa.
            ValidationError: se a nova turma e a mesma da matricula atual.
        """
        if matricula_atual.status != Matricula.Status.ATIVA:
            raise ValidationError(
                f'A matricula do aluno {matricula_atual.aluno} nao esta ativa.'
            )

        if nova_turma == matricula_atual.turma:
            raise ValidationError(
                f'A nova turma nao pode ser a mesma turma atual '
                f'({matricula_atual.turma}).'
            )

        aluno = matricula_atual.aluno
        ano_letivo = matricula_atual.ano_letivo

        # Encerra a matricula atual
        matricula_atual.status = Matricula.Status.ENCERRADA
        matricula_atual.save(update_fields=['status', 'atualizado_em'])

        # Desativa o AlunoTurma antigo
        AlunoTurma.objects.filter(
            aluno=aluno,
            turma=matricula_atual.turma,
        ).update(ativo=False)

        # Movimentacao de saida
        MovimentacaoAluno.objects.create(
            aluno=aluno,
            tipo_evento=MovimentacaoAluno.TipoEvento.TRANSFERENCIA_SAIDA,
            data=data,
            descricao=(
                f'Transferencia — saida da turma {matricula_atual.turma} '
                f'para {nova_turma}.'
                f'{" " + observacao if observacao else ""}'
            ),
            matricula=matricula_atual,
        )

        # Cria nova matricula (tipo transferencia)
        nova_matricula = Matricula.objects.create(
            aluno=aluno,
            turma=nova_turma,
            ano_letivo=ano_letivo,
            data_matricula=data,
            tipo=Matricula.Tipo.TRANSFERENCIA,
            status=Matricula.Status.ATIVA,
            observacao=observacao,
        )

        # Cria/atualiza o AlunoTurma novo
        AlunoTurma.objects.update_or_create(
            aluno=aluno,
            turma=nova_turma,
            defaults={
                'data_matricula': data,
                'ativo': True,
            },
        )

        # Movimentacao de entrada
        MovimentacaoAluno.objects.create(
            aluno=aluno,
            tipo_evento=MovimentacaoAluno.TipoEvento.TRANSFERENCIA_ENTRADA,
            data=data,
            descricao=(
                f'Transferencia — entrada na turma {nova_turma} '
                f'(vindo de {matricula_atual.turma}).'
                f'{" " + observacao if observacao else ""}'
            ),
            matricula=nova_matricula,
        )

        return nova_matricula
