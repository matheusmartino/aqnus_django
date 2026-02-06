"""
academic.forms.grade_horaria_form

Formulario customizado para GradeHoraria.
"""

from django import forms
from django.core.exceptions import ValidationError

from academic.models import GradeHoraria


class GradeHorariaForm(forms.ModelForm):
    class Meta:
        model = GradeHoraria
        fields = '__all__'

    def validate_unique(self):
        try:
            super().validate_unique()
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {}
            if '__all__' in error_dict:
                error_dict['__all__'] = [
                    'Ja existe uma grade ativa para esta turma neste ano letivo. '
                    'Desative a grade existente antes de ativar uma nova.'
                ]
            raise ValidationError(error_dict)

    def clean(self):
        cleaned_data = super().clean()
        turma = cleaned_data.get('turma')
        ano_letivo = cleaned_data.get('ano_letivo')

        if turma and ano_letivo and turma.ano_letivo != ano_letivo:
            raise ValidationError({
                'ano_letivo': (
                    f'A turma {turma} pertence ao ano letivo {turma.ano_letivo}. '
                    f'Selecione o ano letivo correto.'
                )
            })

        return cleaned_data
