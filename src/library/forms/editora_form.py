"""
library.forms.editora_form

Formulario customizado para Editora.
"""

from django import forms

from library.models import Editora


class EditoraForm(forms.ModelForm):
    class Meta:
        model = Editora
        fields = '__all__'
