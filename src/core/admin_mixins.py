"""
core.admin_mixins

Mixin base reutilizavel para o Django Admin do projeto AQNUS.

Toda classe ModelAdmin e InlineModelAdmin do projeto deve herdar de
SemIconesRelacionaisMixin como primeira classe na heranca. Isso garante
que campos FK e O2O nunca exibam botoes de acao (add/change/delete/view).

Este mixin atua na Camada 1 da padronizacao visual (nivel Python).
As Camadas 2 (template override) e 3 (CSS) servem como defesa adicional.

Por que formfield_for_dbfield e nao formfield_for_foreignkey?
─────────────────────────────────────────────────────────────
O Django Admin aplica o RelatedFieldWidgetWrapper em formfield_for_dbfield,
DEPOIS de chamar formfield_for_foreignkey. Se sobrescrevessemos apenas
formfield_for_foreignkey, as flags seriam definidas no widget interno
(ex: AutocompleteSelect) e entao sobrescritas pelo wrapper.
Interceptando formfield_for_dbfield, capturamos o widget ja encapsulado.
"""

from django.contrib.admin.widgets import RelatedFieldWidgetWrapper


class SemIconesRelacionaisMixin:
    """Remove icones de criar/editar/excluir/visualizar de campos FK e O2O.

    Funciona tanto em ModelAdmin quanto em InlineModelAdmin.
    Basta adicionar como primeira classe na heranca:

        class MeuAdmin(SemIconesRelacionaisMixin, admin.ModelAdmin):
            ...

        class MeuInline(SemIconesRelacionaisMixin, admin.TabularInline):
            ...
    """

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if formfield:
            widget = getattr(formfield, 'widget', None)
            if isinstance(widget, RelatedFieldWidgetWrapper):
                widget.can_add_related = False
                widget.can_change_related = False
                widget.can_delete_related = False
                widget.can_view_related = False
        return formfield
