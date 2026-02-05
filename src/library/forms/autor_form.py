"""
library.forms.autor_form

Formulario customizado para Autor.
"""

from django import forms

from library.models import Autor


class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor
        fields = '__all__'
