"""
library.forms.emprestimo_form

Formulario customizado para Emprestimo.
"""

from django import forms
from django.core.exceptions import ValidationError

from library.models import Emprestimo


class EmprestimoForm(forms.ModelForm):
    class Meta:
        model = Emprestimo
        fields = '__all__'

    def validate_unique(self):
        try:
            super().validate_unique()
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {}
            if '__all__' in error_dict:
                error_dict['__all__'] = [
                    'Este exemplar ja possui um emprestimo ativo.'
                ]
            raise ValidationError(error_dict)
