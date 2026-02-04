"""
academic.forms.professor_disciplina_form

Formulario customizado para ProfessorDisciplina.
"""

from django import forms
from django.core.exceptions import ValidationError

from academic.models import ProfessorDisciplina


class ProfessorDisciplinaForm(forms.ModelForm):
    class Meta:
        model = ProfessorDisciplina
        fields = '__all__'

    def validate_unique(self):
        try:
            super().validate_unique()
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {}
            if '__all__' in error_dict:
                error_dict['__all__'] = [
                    'Este professor ja esta vinculado a esta disciplina neste ano letivo.'
                ]
            raise ValidationError(error_dict)
