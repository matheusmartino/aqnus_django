from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from core.admin_mixins import SemIconesRelacionaisMixin
from .forms import (
    AutorForm,
    EditoraForm,
    AssuntoForm,
    ObraForm,
    ExemplarForm,
    EmprestimoForm,
)
from .models import (
    Autor,
    Editora,
    Assunto,
    Obra,
    Exemplar,
    Emprestimo,
)
from .services import BibliotecaService


# ───────────────────────────────────────────────
# Inlines
# ───────────────────────────────────────────────

class ExemplarInline(SemIconesRelacionaisMixin, admin.TabularInline):
    """Mostra exemplares vinculados a uma obra."""
    model = Exemplar
    form = ExemplarForm
    extra = 1
    readonly_fields = ('situacao',)


# ───────────────────────────────────────────────
# Cadastro
# ───────────────────────────────────────────────

@admin.register(Autor)
class AutorAdmin(SemIconesRelacionaisMixin, admin.ModelAdmin):
    form = AutorForm
    list_display = ('nome', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome',)
    list_editable = ('ativo',)
    list_per_page = 25
    fieldsets = (
        ('Identificacao', {
            'fields': ('nome',),
        }),
        ('Status', {
            'fields': ('ativo',),
        }),
    )


@admin.register(Editora)
class EditoraAdmin(SemIconesRelacionaisMixin, admin.ModelAdmin):
    form = EditoraForm
    list_display = ('nome', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome',)
    list_editable = ('ativo',)
    list_per_page = 25
    fieldsets = (
        ('Identificacao', {
            'fields': ('nome',),
        }),
        ('Status', {
            'fields': ('ativo',),
        }),
    )


@admin.register(Assunto)
class AssuntoAdmin(SemIconesRelacionaisMixin, admin.ModelAdmin):
    form = AssuntoForm
    list_display = ('nome', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome',)
    list_editable = ('ativo',)
    list_per_page = 25
    fieldsets = (
        ('Identificacao', {
            'fields': ('nome',),
        }),
        ('Status', {
            'fields': ('ativo',),
        }),
    )


@admin.register(Obra)
class ObraAdmin(SemIconesRelacionaisMixin, admin.ModelAdmin):
    form = ObraForm
    list_display = ('titulo', 'editora', 'assunto', 'ano_publicacao', 'ativa')
    list_filter = ('ativa', 'assunto', 'editora')
    search_fields = ('titulo', 'isbn')
    list_editable = ('ativa',)
    list_per_page = 25
    autocomplete_fields = ('editora', 'assunto')
    filter_horizontal = ('autores',)
    inlines = [ExemplarInline]
    fieldsets = (
        ('Identificacao', {
            'fields': ('titulo', 'isbn', 'ano_publicacao'),
        }),
        ('Classificacao', {
            'fields': ('autores', 'editora', 'assunto'),
        }),
        ('Observacao', {
            'fields': ('observacao',),
            'classes': ('collapse',),
        }),
        ('Status', {
            'fields': ('ativa',),
        }),
    )


@admin.register(Exemplar)
class ExemplarAdmin(SemIconesRelacionaisMixin, admin.ModelAdmin):
    form = ExemplarForm
    list_display = ('codigo_patrimonio', 'obra', 'estado_fisico', 'situacao', 'ativo')
    list_filter = ('situacao', 'estado_fisico', 'ativo')
    search_fields = ('codigo_patrimonio', 'obra__titulo')
    list_editable = ('ativo',)
    list_per_page = 25
    autocomplete_fields = ('obra',)
    readonly_fields = ('situacao',)
    fieldsets = (
        ('Identificacao', {
            'fields': ('obra', 'codigo_patrimonio'),
        }),
        ('Estado', {
            'fields': ('estado_fisico', 'situacao'),
        }),
        ('Status', {
            'fields': ('ativo',),
        }),
    )


# ───────────────────────────────────────────────
# Operacao
# ───────────────────────────────────────────────

@admin.register(Emprestimo)
class EmprestimoAdmin(SemIconesRelacionaisMixin, admin.ModelAdmin):
    form = EmprestimoForm
    list_display = (
        'aluno', 'exemplar', 'data_emprestimo',
        'data_prevista_devolucao', 'status',
    )
    list_filter = ('status',)
    search_fields = (
        'aluno__pessoa__nome',
        'aluno__matricula',
        'exemplar__codigo_patrimonio',
        'exemplar__obra__titulo',
    )
    autocomplete_fields = ('exemplar', 'aluno', 'turma')
    list_per_page = 25
    fieldsets = (
        ('Exemplar e aluno', {
            'fields': ('exemplar', 'aluno', 'turma'),
        }),
        ('Datas', {
            'fields': (
                'data_emprestimo', 'data_prevista_devolucao',
                'data_devolucao', 'status',
            ),
        }),
        ('Observacao', {
            'fields': ('observacao',),
            'classes': ('collapse',),
        }),
    )
    actions = ['devolver_exemplar']

    def save_model(self, request, obj, form, change):
        if not change:
            # Novo emprestimo — usar o service
            try:
                BibliotecaService.emprestar_exemplar(
                    exemplar=obj.exemplar,
                    aluno=obj.aluno,
                    data_emprestimo=obj.data_emprestimo,
                    data_prevista_devolucao=obj.data_prevista_devolucao,
                    turma=obj.turma,
                    observacao=obj.observacao,
                )
                messages.success(request, 'Emprestimo realizado com sucesso.')
            except ValidationError as e:
                messages.error(request, str(e.message))
        else:
            super().save_model(request, obj, form, change)

    @admin.action(description='Devolver exemplar(es) selecionado(s)')
    def devolver_exemplar(self, request, queryset):
        devolvidos = 0
        erros = 0
        for emprestimo in queryset:
            try:
                BibliotecaService.devolver_exemplar(emprestimo)
                devolvidos += 1
            except ValidationError:
                erros += 1

        if devolvidos:
            messages.success(
                request,
                f'{devolvidos} emprestimo(s) devolvido(s) com sucesso.',
            )
        if erros:
            messages.warning(
                request,
                f'{erros} emprestimo(s) nao puderam ser devolvidos '
                f'(ja devolvidos ou invalidos).',
            )

    def has_change_permission(self, request, obj=None):
        if obj and obj.status == Emprestimo.Status.DEVOLVIDO:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status == Emprestimo.Status.DEVOLVIDO:
            return False
        return super().has_delete_permission(request, obj)
