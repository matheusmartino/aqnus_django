"""
library.forms.assunto_form

Formulario customizado para Assunto.
"""

from django import forms
from django.core.exceptions import ValidationError

from library.models import Assunto


class AssuntoForm(forms.ModelForm):
    class Meta:
        model = Assunto
        fields = '__all__'

    def validate_unique(self):
        try:
            super().validate_unique()
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {}
            if '__all__' in error_dict:
                error_dict['__all__'] = [
                    'Ja existe um assunto com este nome.'
                ]
            raise ValidationError(error_dict)
