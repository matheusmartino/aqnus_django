from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from core.admin_mixins import SemIconesRelacionaisMixin
from .forms import (
    AnoLetivoForm,
    DisciplinaForm,
    TurmaForm,
    ProfessorDisciplinaForm,
    AlunoTurmaForm,
    MatriculaForm,
    MovimentacaoAlunoForm,
    HorarioForm,
    GradeHorariaForm,
    GradeItemForm,
)
from .models import (
    AnoLetivo,
    Disciplina,
    Turma,
    ProfessorDisciplina,
    AlunoTurma,
    Matricula,
    MovimentacaoAluno,
    Horario,
    GradeHoraria,
    GradeItem,
)
from .services import GradeService


# ───────────────────────────────────────────────
# Inlines
# ───────────────────────────────────────────────

class AlunoTurmaInline(SemIconesRelacionaisMixin, admin.TabularInline):
    """Permite matricular alunos diretamente na tela da Turma."""
    model = AlunoTurma
    form = AlunoTurmaForm
    extra = 1
    autocomplete_fields = ('aluno',)


class ProfessorDisciplinaInline(SemIconesRelacionaisMixin, admin.TabularInline):
    """Permite vincular professores diretamente na tela da Disciplina."""
    model = ProfessorDisciplina
    form = ProfessorDisciplinaForm
    extra = 1
    autocomplete_fields = ('professor', 'ano_letivo')


class MovimentacaoAlunoInline(SemIconesRelacionaisMixin, admin.TabularInline):
    """Mostra movimentacoes vinculadas a uma matricula."""
    model = MovimentacaoAluno
    form = MovimentacaoAlunoForm
    extra = 0
    readonly_fields = ('tipo_evento', 'data', 'descricao')
    autocomplete_fields = ('aluno',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class MatriculaInlineParaTurma(SemIconesRelacionaisMixin, admin.TabularInline):
    """Mostra matriculas na tela da Turma."""
    model = Matricula
    form = MatriculaForm
    extra = 0
    readonly_fields = ('aluno', 'data_matricula', 'tipo', 'status')
    autocomplete_fields = ('aluno', 'ano_letivo')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ───────────────────────────────────────────────
# ModelAdmins
# ───────────────────────────────────────────────

@admin.register(AnoLetivo)
class AnoLetivoAdmin(SemIconesRelacionaisMixin, admin.ModelAdmin):
    form = AnoLetivoForm
    list_display = ('nome', 'data_inicio', 'data_fim', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome',)
    list_editable = ('ativo',)
    list_per_page = 25
    fieldsets = (
        ('Identificacao', {
            'fields': ('nome',),
        }),
        ('Periodo', {
            'fields': ('data_inicio', 'data_fim'),
        }),
        ('Status', {
            'fields': ('ativo',),
        }),
    )


@admin.register(Disciplina)
class DisciplinaAdmin(SemIconesRelacionaisMixin, admin.ModelAdmin):
    form = DisciplinaForm
    list_display = ('nome', 'codigo', 'carga_horaria', 'ativa')
    list_filter = ('ativa',)
    search_fields = ('nome', 'codigo')
    list_editable = ('ativa',)
    list_per_page = 25
    inlines = [ProfessorDisciplinaInline]
    fieldsets = (
        ('Identificacao', {
            'fields': ('nome', 'codigo'),
        }),
        ('Carga horaria', {
            'fields': ('carga_horaria',),
        }),
        ('Status', {
            'fields': ('ativa',),
        }),
    )


@admin.register(Turma)
class TurmaAdmin(SemIconesRelacionaisMixin, admin.ModelAdmin):
    form = TurmaForm
    list_display = ('nome', 'ano_letivo', 'escola', 'ativa')
    list_filter = ('ativa', 'ano_letivo', 'escola')
    search_fields = ('nome', 'ano_letivo__nome')
    list_editable = ('ativa',)
    list_per_page = 25
    autocomplete_fields = ('ano_letivo', 'escola')
    inlines = [AlunoTurmaInline, MatriculaInlineParaTurma]
    fieldsets = (
        ('Identificacao', {
            'fields': ('nome',),
        }),
        ('Vinculo', {
            'fields': ('ano_letivo', 'escola'),
        }),
        ('Status', {
            'fields': ('ativa',),
        }),
    )


@admin.register(ProfessorDisciplina)
class ProfessorDisciplinaAdmin(SemIconesRelacionaisMixin, admin.ModelAdmin):
    form = ProfessorDisciplinaForm
    list_display = ('professor', 'disciplina', 'ano_letivo')
    list_filter = ('ano_letivo', 'disciplina')
    search_fields = (
        'professor__pessoa__nome',
        'disciplina__nome',
    )
    autocomplete_fields = ('professor', 'disciplina', 'ano_letivo')
    list_per_page = 25


@admin.register(AlunoTurma)
class AlunoTurmaAdmin(SemIconesRelacionaisMixin, admin.ModelAdmin):
    form = AlunoTurmaForm
    list_display = ('aluno', 'turma', 'data_matricula', 'ativo')
    list_filter = ('ativo', 'turma__ano_letivo', 'turma')
    search_fields = (
        'aluno__pessoa__nome',
        'aluno__matricula',
        'turma__nome',
    )
    autocomplete_fields = ('aluno', 'turma')
    list_editable = ('ativo',)
    list_per_page = 25
    fieldsets = (
        (None, {
            'fields': ('aluno', 'turma', 'data_matricula'),
        }),
        ('Status', {
            'fields': ('ativo',),
        }),
    )


@admin.register(Matricula)
class MatriculaAdmin(SemIconesRelacionaisMixin, admin.ModelAdmin):
    form = MatriculaForm
    list_display = ('aluno', 'turma', 'ano_letivo', 'data_matricula',
                    'tipo', 'status')
    list_filter = ('status', 'tipo', 'ano_letivo')
    search_fields = (
        'aluno__pessoa__nome',
        'aluno__matricula',
        'turma__nome',
    )
    autocomplete_fields = ('aluno', 'turma', 'ano_letivo')
    list_per_page = 25
    inlines = [MovimentacaoAlunoInline]
    fieldsets = (
        ('Aluno e turma', {
            'fields': ('aluno', 'turma', 'ano_letivo'),
        }),
        ('Dados da matricula', {
            'fields': ('data_matricula', 'tipo', 'status'),
        }),
        ('Observacao', {
            'fields': ('observacao',),
            'classes': ('collapse',),
        }),
    )


@admin.register(MovimentacaoAluno)
class MovimentacaoAlunoAdmin(SemIconesRelacionaisMixin, admin.ModelAdmin):
    form = MovimentacaoAlunoForm
    list_display = ('aluno', 'tipo_evento', 'data', 'matricula')
    list_filter = ('tipo_evento',)
    search_fields = (
        'aluno__pessoa__nome',
        'descricao',
    )
    autocomplete_fields = ('aluno', 'matricula')
    list_per_page = 25
    readonly_fields = ('aluno', 'tipo_evento', 'data', 'descricao', 'matricula')
    fieldsets = (
        (None, {
            'fields': ('aluno', 'tipo_evento', 'data'),
        }),
        ('Detalhes', {
            'fields': ('descricao', 'matricula'),
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ───────────────────────────────────────────────
# Grade Horaria (Etapa 5)
# ───────────────────────────────────────────────

class GradeItemInline(SemIconesRelacionaisMixin, admin.TabularInline):
    """Permite adicionar aulas diretamente na tela da Grade Horaria."""
    model = GradeItem
    form = GradeItemForm
    extra = 1
    autocomplete_fields = ('horario', 'disciplina', 'professor')
    ordering = ('dia_semana', 'horario__ordem')


@admin.register(Horario)
class HorarioAdmin(SemIconesRelacionaisMixin, admin.ModelAdmin):
    form = HorarioForm
    list_display = ('ordem', 'hora_inicio', 'hora_fim', 'turno')
    list_filter = ('turno',)
    search_fields = ('ordem',)
    list_per_page = 25
    ordering = ('turno', 'ordem')
    fieldsets = (
        ('Identificacao', {
            'fields': ('ordem', 'turno'),
        }),
        ('Horarios', {
            'fields': ('hora_inicio', 'hora_fim'),
        }),
    )


@admin.register(GradeHoraria)
class GradeHorariaAdmin(SemIconesRelacionaisMixin, admin.ModelAdmin):
    form = GradeHorariaForm
    list_display = ('turma', 'ano_letivo', 'ativa', 'qtd_aulas')
    list_filter = ('ativa', 'ano_letivo')
    search_fields = ('turma__nome', 'ano_letivo__nome')
    list_editable = ('ativa',)
    list_per_page = 25
    autocomplete_fields = ('turma', 'ano_letivo')
    inlines = [GradeItemInline]
    fieldsets = (
        ('Vinculo', {
            'fields': ('turma', 'ano_letivo'),
        }),
        ('Status', {
            'fields': ('ativa',),
        }),
        ('Observacao', {
            'fields': ('observacao',),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Aulas')
    def qtd_aulas(self, obj):
        return obj.itens.count()

    def save_formset(self, request, form, formset, change):
        """Valida itens da grade via GradeService antes de salvar."""
        instances = formset.save(commit=False)

        for instance in instances:
            if isinstance(instance, GradeItem):
                try:
                    # Valida habilitacao do professor
                    GradeService.validar_habilitacao_professor(
                        instance.professor,
                        instance.disciplina,
                        instance.grade_horaria.ano_letivo,
                    )

                    # Valida conflito de professor
                    GradeService.validar_conflito_professor(
                        instance.professor,
                        instance.dia_semana,
                        instance.horario,
                        instance.grade_horaria.ano_letivo,
                        excluir_item_id=instance.pk,
                    )

                    # Valida conflito de turma (ja coberto pela constraint,
                    # mas mensagem e mais clara)
                    GradeService.validar_conflito_turma(
                        instance.grade_horaria,
                        instance.dia_semana,
                        instance.horario,
                        excluir_item_id=instance.pk,
                    )

                    instance.save()

                except ValidationError as e:
                    messages.error(request, str(e.message))
            else:
                instance.save()

        # Processa deletes
        for obj in formset.deleted_objects:
            obj.delete()

        formset.save_m2m()


@admin.register(GradeItem)
class GradeItemAdmin(SemIconesRelacionaisMixin, admin.ModelAdmin):
    form = GradeItemForm
    list_display = ('grade_horaria', 'dia_semana_display', 'horario',
                    'disciplina', 'professor')
    list_filter = ('dia_semana', 'grade_horaria__ano_letivo',
                   'grade_horaria__turma')
    search_fields = (
        'grade_horaria__turma__nome',
        'disciplina__nome',
        'professor__pessoa__nome',
    )
    autocomplete_fields = ('grade_horaria', 'horario', 'disciplina', 'professor')
    list_per_page = 25
    fieldsets = (
        ('Grade', {
            'fields': ('grade_horaria',),
        }),
        ('Alocacao', {
            'fields': ('dia_semana', 'horario'),
        }),
        ('Aula', {
            'fields': ('disciplina', 'professor'),
        }),
    )

    @admin.display(description='Dia', ordering='dia_semana')
    def dia_semana_display(self, obj):
        return obj.get_dia_semana_display()

    def save_model(self, request, obj, form, change):
        """Valida via GradeService antes de salvar."""
        try:
            # Valida habilitacao do professor
            GradeService.validar_habilitacao_professor(
                obj.professor,
                obj.disciplina,
                obj.grade_horaria.ano_letivo,
            )

            # Valida conflito de professor
            GradeService.validar_conflito_professor(
                obj.professor,
                obj.dia_semana,
                obj.horario,
                obj.grade_horaria.ano_letivo,
                excluir_item_id=obj.pk if change else None,
            )

            # Valida conflito de turma
            GradeService.validar_conflito_turma(
                obj.grade_horaria,
                obj.dia_semana,
                obj.horario,
                excluir_item_id=obj.pk if change else None,
            )

            super().save_model(request, obj, form, change)
            messages.success(request, f'Aula salva com sucesso: {obj}')

        except ValidationError as e:
            messages.error(request, str(e.message))
