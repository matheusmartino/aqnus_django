"""
academic.forms.grade_item_form

Formulario customizado para GradeItem.
"""

from django import forms
from django.core.exceptions import ValidationError

from academic.models import GradeItem


class GradeItemForm(forms.ModelForm):
    class Meta:
        model = GradeItem
        fields = '__all__'

    def validate_unique(self):
        try:
            super().validate_unique()
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {}
            if '__all__' in error_dict:
                error_dict['__all__'] = [
                    'Ja existe uma aula neste dia e horario para esta grade. '
                    'Cada slot de horario so pode ter uma disciplina.'
                ]
            raise ValidationError(error_dict)
