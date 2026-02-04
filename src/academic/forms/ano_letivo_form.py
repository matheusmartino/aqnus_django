"""
academic.forms.ano_letivo_form

Formulario customizado para AnoLetivo.
"""

from django import forms
from django.core.exceptions import ValidationError

from academic.models import AnoLetivo


class AnoLetivoForm(forms.ModelForm):
    class Meta:
        model = AnoLetivo
        fields = '__all__'

    def validate_unique(self):
        try:
            super().validate_unique()
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {}
            if 'nome' in error_dict:
                error_dict['nome'] = [
                    'Ja existe um ano letivo cadastrado com este nome.'
                ]
            raise ValidationError(error_dict)
