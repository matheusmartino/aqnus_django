"""
people.forms.aluno_responsavel_form

Formulario customizado para AlunoResponsavel.
"""

from django import forms
from django.core.exceptions import ValidationError

from people.models import AlunoResponsavel


class AlunoResponsavelForm(forms.ModelForm):
    class Meta:
        model = AlunoResponsavel
        fields = '__all__'

    def validate_unique(self):
        try:
            super().validate_unique()
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {}
            if '__all__' in error_dict:
                error_dict['__all__'] = [
                    'Este responsavel ja esta vinculado a este aluno.'
                ]
            raise ValidationError(error_dict)
