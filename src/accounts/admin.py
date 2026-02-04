from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.admin_mixins import SemIconesRelacionaisMixin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(SemIconesRelacionaisMixin, UserAdmin):
    list_display = ('username', 'get_full_name', 'email', 'papel', 'is_active', 'is_staff')
    list_filter = ('papel', 'is_active', 'is_staff', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_per_page = 25
    autocomplete_fields = ('pessoa',)

    # Adiciona os campos customizados ao formulario de edicao
    fieldsets = UserAdmin.fieldsets + (
        ('AQNUS', {
            'fields': ('pessoa', 'papel'),
        }),
    )

    # Adiciona os campos customizados ao formulario de criacao
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('AQNUS', {
            'fields': ('pessoa', 'papel'),
        }),
    )
