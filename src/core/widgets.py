"""
core.widgets

Widget customizado para campos relacionais no Django Admin AQNUS.

O Django Admin envolve todo campo FK e O2O com RelatedFieldWidgetWrapper,
que renderiza botoes de adicionar/editar/excluir/visualizar ao lado do campo.
Este modulo fornece um wrapper alternativo que desabilita TODOS esses botoes.

Camada 1 da padronizacao visual — atua no nivel do widget Python.
Complementado pela Camada 2 (template override) e Camada 3 (CSS).
"""

from django.contrib.admin.widgets import RelatedFieldWidgetWrapper


class SemAcoesWidgetWrapper(RelatedFieldWidgetWrapper):
    """RelatedFieldWidgetWrapper com todas as acoes desabilitadas.

    Forca can_add_related, can_change_related, can_delete_related e
    can_view_related para False, independente das permissoes do usuario.

    Uso direto (raro — o SemIconesRelacionaisMixin ja aplica automaticamente):

        formfield.widget = SemAcoesWidgetWrapper(
            formfield.widget,
            db_field.remote_field,
            self.admin_site,
        )
    """

    def __init__(self, widget, rel, admin_site, **kwargs):
        kwargs['can_add_related'] = False
        kwargs['can_change_related'] = False
        kwargs['can_delete_related'] = False
        kwargs['can_view_related'] = False
        super().__init__(widget, rel, admin_site, **kwargs)
        # Garante flags desativadas apos o processamento interno do super
        self.can_add_related = False
        self.can_change_related = False
        self.can_delete_related = False
        self.can_view_related = False
