"""
academic.forms.disciplina_form

Formulario customizado para Disciplina.
"""

from django import forms
from django.core.exceptions import ValidationError

from academic.models import Disciplina


class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = '__all__'

    def validate_unique(self):
        try:
            super().validate_unique()
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {}
            if 'codigo' in error_dict:
                error_dict['codigo'] = [
                    'Ja existe uma disciplina cadastrada com este codigo.'
                ]
            raise ValidationError(error_dict)
