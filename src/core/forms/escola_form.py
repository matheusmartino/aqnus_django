"""
core.forms.escola_form

Formulario customizado para Escola.
"""

from django import forms
from django.core.exceptions import ValidationError

from core.models import Escola


class EscolaForm(forms.ModelForm):
    class Meta:
        model = Escola
        fields = '__all__'

    def validate_unique(self):
        try:
            super().validate_unique()
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {}
            if 'cnpj' in error_dict:
                error_dict['cnpj'] = [
                    'Ja existe uma escola cadastrada com este CNPJ.'
                ]
            raise ValidationError(error_dict)
