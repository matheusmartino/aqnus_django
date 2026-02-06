"""
web.views.mixins

Mixins reutilizaveis para views do front operacional.
"""

from django import forms as django_forms


class WebMixin:
    """Mixin base que injeta active_menu no contexto."""

    active_menu = ''

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_menu'] = self.active_menu
        return ctx


class BootstrapFormMixin:
    """
    Mixin que adiciona classes Bootstrap 5 aos widgets do form.

    Aplica automaticamente:
    - form-control em inputs de texto, numero, email, etc.
    - form-select em selects e selects multiplos
    - form-check-input em checkboxes
    - type="date" em campos DateField
    - is-invalid em campos com erro (form bound)
    """

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        for field_name, field in form.fields.items():
            widget = field.widget

            if isinstance(widget, django_forms.CheckboxInput):
                widget.attrs.setdefault('class', 'form-check-input')

            elif isinstance(widget, django_forms.SelectMultiple):
                widget.attrs.setdefault('class', 'form-select')
                widget.attrs.setdefault('size', '5')

            elif isinstance(widget, django_forms.Select):
                widget.attrs.setdefault('class', 'form-select')

            elif isinstance(widget, django_forms.Textarea):
                widget.attrs.setdefault('class', 'form-control')
                widget.attrs.setdefault('rows', '3')

            elif isinstance(field, django_forms.DateField):
                field.widget = django_forms.DateInput(
                    attrs={'type': 'date', 'class': 'form-control'},
                    format='%Y-%m-%d',
                )

            else:
                widget.attrs.setdefault('class', 'form-control')

        # Adiciona is-invalid em campos com erro
        if form.is_bound and form.errors:
            for field_name in form.errors:
                if field_name != '__all__' and field_name in form.fields:
                    css = form.fields[field_name].widget.attrs.get('class', '')
                    if 'is-invalid' not in css:
                        form.fields[field_name].widget.attrs['class'] = (
                            f'{css} is-invalid'.strip()
                        )

        return form
