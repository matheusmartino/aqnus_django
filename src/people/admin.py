from django.contrib import admin

from core.admin_mixins import SemIconesRelacionaisMixin
from .forms import PessoaForm, AlunoForm, ProfessorForm, FuncionarioForm
from .models import Aluno, Funcionario, Pessoa, Professor


# ───────────────────────────────────────────────
# Inlines — permitem editar perfis diretamente na tela de Pessoa
# ───────────────────────────────────────────────

class AlunoInline(SemIconesRelacionaisMixin, admin.StackedInline):
    model = Aluno
    extra = 0
    verbose_name = 'perfil de aluno'
    verbose_name_plural = 'perfil de aluno'


class ProfessorInline(SemIconesRelacionaisMixin, admin.StackedInline):
    model = Professor
    extra = 0
    verbose_name = 'perfil de professor'
    verbose_name_plural = 'perfil de professor'


class FuncionarioInline(SemIconesRelacionaisMixin, admin.StackedInline):
    model = Funcionario
    extra = 0
    verbose_name = 'perfil de funcionario'
    verbose_name_plural = 'perfil de funcionario'


# ───────────────────────────────────────────────
# ModelAdmins
# ───────────────────────────────────────────────

@admin.register(Pessoa)
class PessoaAdmin(SemIconesRelacionaisMixin, admin.ModelAdmin):
    form = PessoaForm
    list_display = ('nome', 'cpf', 'email', 'telefone', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome', 'cpf', 'email')
    list_editable = ('ativo',)
    list_per_page = 25
    inlines = [AlunoInline, ProfessorInline, FuncionarioInline]
    fieldsets = (
        ('Identificacao', {
            'fields': ('nome', 'cpf', 'data_nascimento'),
        }),
        ('Contato', {
            'fields': ('telefone', 'email'),
        }),
        ('Endereco', {
            'fields': ('endereco',),
        }),
        ('Status', {
            'fields': ('ativo',),
        }),
    )


@admin.register(Aluno)
class AlunoAdmin(SemIconesRelacionaisMixin, admin.ModelAdmin):
    form = AlunoForm
    list_display = ('pessoa', 'matricula', 'data_ingresso', 'situacao')
    list_filter = ('situacao',)
    search_fields = ('pessoa__nome', 'matricula')
    list_per_page = 25
    autocomplete_fields = ('pessoa',)
    fieldsets = (
        ('Vinculo', {
            'fields': ('pessoa',),
        }),
        ('Dados academicos', {
            'fields': ('matricula', 'data_ingresso', 'situacao'),
        }),
    )


@admin.register(Professor)
class ProfessorAdmin(SemIconesRelacionaisMixin, admin.ModelAdmin):
    form = ProfessorForm
    list_display = ('pessoa', 'formacao', 'carga_horaria_max', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('pessoa__nome', 'formacao')
    list_editable = ('ativo',)
    list_per_page = 25
    autocomplete_fields = ('pessoa',)
    fieldsets = (
        ('Vinculo', {
            'fields': ('pessoa',),
        }),
        ('Dados profissionais', {
            'fields': ('formacao', 'carga_horaria_max'),
        }),
        ('Status', {
            'fields': ('ativo',),
        }),
    )


@admin.register(Funcionario)
class FuncionarioAdmin(SemIconesRelacionaisMixin, admin.ModelAdmin):
    form = FuncionarioForm
    list_display = ('pessoa', 'cargo', 'setor', 'ativo')
    list_filter = ('ativo', 'setor')
    search_fields = ('pessoa__nome', 'cargo', 'setor')
    list_editable = ('ativo',)
    list_per_page = 25
    autocomplete_fields = ('pessoa',)
    fieldsets = (
        ('Vinculo', {
            'fields': ('pessoa',),
        }),
        ('Dados funcionais', {
            'fields': ('cargo', 'setor'),
        }),
        ('Status', {
            'fields': ('ativo',),
        }),
    )
