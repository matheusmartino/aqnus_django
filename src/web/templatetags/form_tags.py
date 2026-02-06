"""
web.templatetags.form_tags

Filtros de template para renderizacao de formularios com Bootstrap 5.
"""

from django import forms, template

register = template.Library()


@register.filter
def widget_type(field):
    """
    Retorna o tipo de widget de um campo para uso condicional no template.

    Valores possiveis: checkbox, select_multiple, select, textarea, date, text.
    """
    widget = field.field.widget
    if isinstance(widget, forms.CheckboxInput):
        return 'checkbox'
    if isinstance(widget, forms.SelectMultiple):
        return 'select_multiple'
    if isinstance(widget, forms.Select):
        return 'select'
    if isinstance(widget, forms.Textarea):
        return 'textarea'
    if isinstance(widget, forms.DateInput):
        return 'date'
    return 'text'
