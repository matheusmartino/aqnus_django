"""
academic.services.grade_service

Regras de negocio para grade horaria escolar.

Toda operacao que crie ou altere itens na grade horaria deve passar por
este service. Admin e views NUNCA devem manipular GradeItem diretamente
sem passar pelas validacoes aqui definidas.
"""

from django.core.exceptions import ValidationError
from django.db import transaction

from academic.models import GradeHoraria, GradeItem, ProfessorDisciplina


class GradeService:
    """Centraliza operacoes de grade horaria."""

    @staticmethod
    def validar_habilitacao_professor(professor, disciplina, ano_letivo):
        """
        Valida se o professor esta habilitado para lecionar a disciplina
        no ano letivo especificado.

        Raises:
            ValidationError: se o professor nao esta habilitado.
        """
        habilitado = ProfessorDisciplina.objects.filter(
            professor=professor,
            disciplina=disciplina,
            ano_letivo=ano_letivo,
        ).exists()

        if not habilitado:
            raise ValidationError(
                f'O professor {professor} nao esta habilitado para lecionar '
                f'{disciplina} no ano letivo {ano_letivo}. '
                f'Registre o vinculo em Professor-Disciplina antes de alocar na grade.'
            )

    @staticmethod
    def validar_conflito_professor(professor, dia_semana, horario, ano_letivo,
                                   excluir_item_id=None):
        """
        Valida se o professor nao possui outra aula no mesmo dia/horario.

        Verifica todas as grades ativas do ano letivo para detectar conflito.

        Args:
            professor: instancia de Professor
            dia_semana: string do dia (DiaSemana)
            horario: instancia de Horario
            ano_letivo: instancia de AnoLetivo
            excluir_item_id: ID de GradeItem a ignorar (para edicao)

        Raises:
            ValidationError: se houver conflito.
        """
        conflito = GradeItem.objects.filter(
            professor=professor,
            dia_semana=dia_semana,
            horario=horario,
            grade_horaria__ano_letivo=ano_letivo,
            grade_horaria__ativa=True,
        )

        if excluir_item_id:
            conflito = conflito.exclude(id=excluir_item_id)

        conflito = conflito.select_related(
            'grade_horaria__turma',
            'disciplina',
        ).first()

        if conflito:
            raise ValidationError(
                f'Conflito de horario: o professor {professor} ja esta alocado '
                f'na turma {conflito.grade_horaria.turma} '
                f'({conflito.disciplina}) no mesmo dia e horario.'
            )

    @staticmethod
    def validar_conflito_turma(grade_horaria, dia_semana, horario,
                               excluir_item_id=None):
        """
        Valida se a turma nao possui outra aula no mesmo dia/horario.

        Args:
            grade_horaria: instancia de GradeHoraria
            dia_semana: string do dia (DiaSemana)
            horario: instancia de Horario
            excluir_item_id: ID de GradeItem a ignorar (para edicao)

        Raises:
            ValidationError: se houver conflito.
        """
        conflito = GradeItem.objects.filter(
            grade_horaria=grade_horaria,
            dia_semana=dia_semana,
            horario=horario,
        )

        if excluir_item_id:
            conflito = conflito.exclude(id=excluir_item_id)

        conflito = conflito.select_related('disciplina', 'professor').first()

        if conflito:
            raise ValidationError(
                f'Conflito de horario: a turma {grade_horaria.turma} ja possui '
                f'aula de {conflito.disciplina} com {conflito.professor} '
                f'no mesmo dia e horario.'
            )

    @staticmethod
    @transaction.atomic
    def adicionar_aula(grade_horaria, dia_semana, horario, disciplina, professor):
        """
        Adiciona uma aula a grade horaria.

        Valida todas as regras de negocio antes de criar o item.

        Args:
            grade_horaria: instancia de GradeHoraria
            dia_semana: string do dia (DiaSemana)
            horario: instancia de Horario
            disciplina: instancia de Disciplina
            professor: instancia de Professor

        Returns:
            GradeItem criado.

        Raises:
            ValidationError: se alguma regra de negocio for violada.
        """
        ano_letivo = grade_horaria.ano_letivo

        # Valida habilitacao do professor
        GradeService.validar_habilitacao_professor(
            professor, disciplina, ano_letivo
        )

        # Valida conflito de horario do professor
        GradeService.validar_conflito_professor(
            professor, dia_semana, horario, ano_letivo
        )

        # Valida conflito de horario da turma
        GradeService.validar_conflito_turma(
            grade_horaria, dia_semana, horario
        )

        # Cria o item
        item = GradeItem.objects.create(
            grade_horaria=grade_horaria,
            dia_semana=dia_semana,
            horario=horario,
            disciplina=disciplina,
            professor=professor,
        )

        return item

    @staticmethod
    @transaction.atomic
    def atualizar_aula(item, dia_semana=None, horario=None, disciplina=None,
                       professor=None):
        """
        Atualiza uma aula existente na grade horaria.

        Valida todas as regras de negocio antes de atualizar.

        Args:
            item: instancia de GradeItem a ser atualizada
            dia_semana: novo dia (opcional)
            horario: novo horario (opcional)
            disciplina: nova disciplina (opcional)
            professor: novo professor (opcional)

        Returns:
            GradeItem atualizado.

        Raises:
            ValidationError: se alguma regra de negocio for violada.
        """
        # Monta valores finais (usa atual se nao informado)
        dia_semana_final = dia_semana if dia_semana else item.dia_semana
        horario_final = horario if horario else item.horario
        disciplina_final = disciplina if disciplina else item.disciplina
        professor_final = professor if professor else item.professor

        ano_letivo = item.grade_horaria.ano_letivo

        # Valida habilitacao do professor (se mudou disciplina ou professor)
        if disciplina or professor:
            GradeService.validar_habilitacao_professor(
                professor_final, disciplina_final, ano_letivo
            )

        # Valida conflito de horario do professor (se mudou dia, horario ou professor)
        if dia_semana or horario or professor:
            GradeService.validar_conflito_professor(
                professor_final, dia_semana_final, horario_final, ano_letivo,
                excluir_item_id=item.id
            )

        # Valida conflito de horario da turma (se mudou dia ou horario)
        if dia_semana or horario:
            GradeService.validar_conflito_turma(
                item.grade_horaria, dia_semana_final, horario_final,
                excluir_item_id=item.id
            )

        # Atualiza o item
        item.dia_semana = dia_semana_final
        item.horario = horario_final
        item.disciplina = disciplina_final
        item.professor = professor_final
        item.save()

        return item

    @staticmethod
    @transaction.atomic
    def remover_aula(item):
        """
        Remove uma aula da grade horaria.

        Args:
            item: instancia de GradeItem a ser removida.
        """
        item.delete()

    @staticmethod
    @transaction.atomic
    def criar_grade(turma, ano_letivo, ativa=True, observacao=''):
        """
        Cria uma nova grade horaria para uma turma.

        Se a grade for criada como ativa, desativa outras grades ativas
        da mesma turma/ano para manter consistencia.

        Args:
            turma: instancia de Turma
            ano_letivo: instancia de AnoLetivo
            ativa: se a grade deve ser ativada
            observacao: texto livre

        Returns:
            GradeHoraria criada.

        Raises:
            ValidationError: se a turma nao pertence ao ano letivo.
        """
        if turma.ano_letivo != ano_letivo:
            raise ValidationError(
                f'A turma {turma} pertence ao ano letivo {turma.ano_letivo}, '
                f'nao pode criar grade para {ano_letivo}.'
            )

        # Se ativa, desativa outras grades da mesma turma/ano
        if ativa:
            GradeHoraria.objects.filter(
                turma=turma,
                ano_letivo=ano_letivo,
                ativa=True,
            ).update(ativa=False)

        grade = GradeHoraria.objects.create(
            turma=turma,
            ano_letivo=ano_letivo,
            ativa=ativa,
            observacao=observacao,
        )

        return grade

    @staticmethod
    @transaction.atomic
    def ativar_grade(grade):
        """
        Ativa uma grade horaria, desativando outras da mesma turma/ano.

        Args:
            grade: instancia de GradeHoraria a ser ativada.
        """
        if grade.ativa:
            return

        # Desativa outras grades da mesma turma/ano
        GradeHoraria.objects.filter(
            turma=grade.turma,
            ano_letivo=grade.ano_letivo,
            ativa=True,
        ).update(ativa=False)

        grade.ativa = True
        grade.save(update_fields=['ativa', 'atualizado_em'])

    @staticmethod
    def obter_grade_ativa(turma, ano_letivo):
        """
        Retorna a grade ativa de uma turma em um ano letivo.

        Args:
            turma: instancia de Turma
            ano_letivo: instancia de AnoLetivo

        Returns:
            GradeHoraria ou None se nao existir.
        """
        return GradeHoraria.objects.filter(
            turma=turma,
            ano_letivo=ano_letivo,
            ativa=True,
        ).prefetch_related(
            'itens__horario',
            'itens__disciplina',
            'itens__professor',
        ).first()
