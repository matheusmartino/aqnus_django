"""
people.forms.responsavel_form

Formulario customizado para Responsavel.
"""

from django import forms
from django.core.exceptions import ValidationError

from people.models import Responsavel


class ResponsavelForm(forms.ModelForm):
    class Meta:
        model = Responsavel
        fields = '__all__'

    def validate_unique(self):
        try:
            super().validate_unique()
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {}
            if 'pessoa' in error_dict:
                error_dict['pessoa'] = [
                    'Esta pessoa ja possui um perfil de responsavel.'
                ]
            raise ValidationError(error_dict)
