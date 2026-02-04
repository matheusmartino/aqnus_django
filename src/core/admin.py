from django.contrib import admin

from .admin_mixins import SemIconesRelacionaisMixin
from .forms import EscolaForm
from .models import Escola


@admin.register(Escola)
class EscolaAdmin(SemIconesRelacionaisMixin, admin.ModelAdmin):
    form = EscolaForm
    list_display = ('nome', 'cnpj', 'telefone', 'email', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome', 'cnpj', 'email')
    list_editable = ('ativo',)
    list_per_page = 25
    fieldsets = (
        ('Identificacao', {
            'fields': ('nome', 'cnpj'),
        }),
        ('Contato', {
            'fields': ('telefone', 'email', 'endereco'),
        }),
        ('Status', {
            'fields': ('ativo',),
        }),
    )
