"""
academic.forms.turma_form

Formulario customizado para Turma.
"""

from django import forms
from django.core.exceptions import ValidationError

from academic.models import Turma


class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = '__all__'

    def validate_unique(self):
        try:
            super().validate_unique()
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {}
            if '__all__' in error_dict:
                error_dict['__all__'] = [
                    'Ja existe uma turma com este nome neste ano letivo e escola.'
                ]
            raise ValidationError(error_dict)
