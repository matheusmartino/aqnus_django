"""
library.forms.obra_form

Formulario customizado para Obra.
"""

from django import forms
from django.core.exceptions import ValidationError

from library.models import Obra


class ObraForm(forms.ModelForm):
    class Meta:
        model = Obra
        fields = '__all__'

    def validate_unique(self):
        try:
            super().validate_unique()
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {}
            if '__all__' in error_dict:
                error_dict['__all__'] = [
                    'Ja existe uma obra com este ISBN.'
                ]
            raise ValidationError(error_dict)
