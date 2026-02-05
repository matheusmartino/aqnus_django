"""
library.forms.exemplar_form

Formulario customizado para Exemplar.
"""

from django import forms
from django.core.exceptions import ValidationError

from library.models import Exemplar


class ExemplarForm(forms.ModelForm):
    class Meta:
        model = Exemplar
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Situacao e controlada pelo service, nao pelo usuario
        if 'situacao' in self.fields:
            self.fields['situacao'].disabled = True

    def validate_unique(self):
        try:
            super().validate_unique()
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {}
            if 'codigo_patrimonio' in error_dict:
                error_dict['codigo_patrimonio'] = [
                    'Ja existe um exemplar com este codigo de patrimonio.'
                ]
            raise ValidationError(error_dict)
