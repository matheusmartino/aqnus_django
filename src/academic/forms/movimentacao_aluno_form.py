"""
academic.forms.movimentacao_aluno_form

Formulario customizado para MovimentacaoAluno.
"""

from django import forms

from academic.models import MovimentacaoAluno


class MovimentacaoAlunoForm(forms.ModelForm):
    class Meta:
        model = MovimentacaoAluno
        fields = '__all__'
