"""
people.forms.aluno_form

Formulario customizado para Aluno.
"""

from django import forms
from django.core.exceptions import ValidationError

from people.models import Aluno


class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = '__all__'

    def validate_unique(self):
        try:
            super().validate_unique()
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {}
            if 'matricula' in error_dict:
                error_dict['matricula'] = [
                    'Ja existe um aluno cadastrado com esta matricula.'
                ]
            if 'pessoa' in error_dict:
                error_dict['pessoa'] = [
                    'Esta pessoa ja possui um perfil de aluno.'
                ]
            raise ValidationError(error_dict)
