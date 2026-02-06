"""
web.views.aluno_views

Views CRUD de alunos.
"""

from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from people.forms import AlunoForm
from people.models import Aluno

from .mixins import BootstrapFormMixin, WebMixin


class AlunoListView(WebMixin, ListView):
    model = Aluno
    template_name = 'pages/alunos/list.html'
    context_object_name = 'alunos'
    active_menu = 'alunos'

    def get_queryset(self):
        qs = Aluno.objects.select_related('pessoa').all()
        query = self.request.GET.get('q', '').strip()
        if query:
            qs = qs.filter(
                Q(pessoa__nome__icontains=query) | Q(matricula__icontains=query)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['query'] = self.request.GET.get('q', '')
        ctx['create_url'] = reverse_lazy('web:aluno_create')

        # Adiciona turma atual para cada aluno
        for aluno in ctx['alunos']:
            vinculo = aluno.turmas_matriculadas.filter(
                ativo=True,
            ).select_related('turma').first()
            aluno.turma_atual = vinculo.turma if vinculo else None

        return ctx


class AlunoCreateView(WebMixin, BootstrapFormMixin, SuccessMessageMixin, CreateView):
    model = Aluno
    form_class = AlunoForm
    template_name = 'pages/alunos/form.html'
    success_url = reverse_lazy('web:alunos_list')
    success_message = 'Aluno criado com sucesso.'
    active_menu = 'alunos'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Novo Aluno'
        ctx['cancel_url'] = reverse_lazy('web:alunos_list')
        return ctx


class AlunoUpdateView(WebMixin, BootstrapFormMixin, SuccessMessageMixin, UpdateView):
    model = Aluno
    form_class = AlunoForm
    template_name = 'pages/alunos/form.html'
    success_url = reverse_lazy('web:alunos_list')
    success_message = 'Aluno atualizado com sucesso.'
    active_menu = 'alunos'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Editar Aluno — {self.object}'
        ctx['cancel_url'] = reverse_lazy('web:alunos_list')
        return ctx
