"""
people.forms.funcionario_form

Formulario customizado para Funcionario.
"""

from django import forms
from django.core.exceptions import ValidationError

from people.models import Funcionario


class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = '__all__'

    def validate_unique(self):
        try:
            super().validate_unique()
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {}
            if 'pessoa' in error_dict:
                error_dict['pessoa'] = [
                    'Esta pessoa ja possui um perfil de funcionario.'
                ]
            raise ValidationError(error_dict)
