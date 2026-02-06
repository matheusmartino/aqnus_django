"""
academic.forms.horario_form

Formulario customizado para Horario.
"""

from django import forms
from django.core.exceptions import ValidationError

from academic.models import Horario


class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = '__all__'

    def validate_unique(self):
        try:
            super().validate_unique()
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {}
            if '__all__' in error_dict:
                error_dict['__all__'] = [
                    'Ja existe um horario com esta ordem neste turno.'
                ]
            raise ValidationError(error_dict)

    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fim = cleaned_data.get('hora_fim')

        if hora_inicio and hora_fim and hora_inicio >= hora_fim:
            raise ValidationError({
                'hora_fim': 'A hora de fim deve ser maior que a hora de inicio.'
            })

        return cleaned_data
