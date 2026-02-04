"""
people.forms.pessoa_form

Formulario customizado para Pessoa.
"""

from django import forms
from django.core.exceptions import ValidationError

from people.models import Pessoa


class PessoaForm(forms.ModelForm):
    class Meta:
        model = Pessoa
        fields = '__all__'

    def validate_unique(self):
        try:
            super().validate_unique()
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {}
            if 'cpf' in error_dict:
                error_dict['cpf'] = [
                    'Ja existe uma pessoa cadastrada com este CPF.'
                ]
            raise ValidationError(error_dict)
