"""
academic.forms.aluno_turma_form

Formulario customizado para AlunoTurma.
"""

from django import forms
from django.core.exceptions import ValidationError

from academic.models import AlunoTurma


class AlunoTurmaForm(forms.ModelForm):
    class Meta:
        model = AlunoTurma
        fields = '__all__'

    def validate_unique(self):
        try:
            super().validate_unique()
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {}
            if '__all__' in error_dict:
                error_dict['__all__'] = [
                    'Este aluno ja esta matriculado nesta turma.'
                ]
            raise ValidationError(error_dict)
