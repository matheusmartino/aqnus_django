from django.contrib import admin

from core.admin_mixins import SemIconesRelacionaisMixin
from .forms import (
    AnoLetivoForm,
    DisciplinaForm,
    TurmaForm,
    ProfessorDisciplinaForm,
    AlunoTurmaForm,
)
from .models import (
    AnoLetivo,
    Disciplina,
    Turma,
    ProfessorDisciplina,
    AlunoTurma,
)


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
    inlines = [AlunoTurmaInline]
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
