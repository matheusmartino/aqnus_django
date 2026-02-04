"""
academic.forms.matricula_form

Formulario customizado para Matricula.
"""

from django import forms
from django.core.exceptions import ValidationError

from academic.models import Matricula


class MatriculaForm(forms.ModelForm):
    class Meta:
        model = Matricula
        fields = '__all__'

    def validate_unique(self):
        try:
            super().validate_unique()
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {}
            if '__all__' in error_dict:
                error_dict['__all__'] = [
                    'Este aluno ja possui uma matricula ativa neste ano letivo.'
                ]
            raise ValidationError(error_dict)
