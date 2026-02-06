"""
web.views.turma_views

Views CRUD de turmas.
"""

from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from academic.forms import TurmaForm
from academic.models import Turma

from .mixins import BootstrapFormMixin, WebMixin


class TurmaListView(WebMixin, ListView):
    model = Turma
    template_name = 'pages/turmas/list.html'
    context_object_name = 'turmas'
    active_menu = 'turmas'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['create_url'] = reverse_lazy('web:turma_create')
        return ctx

    def get_queryset(self):
        return (
            Turma.objects
            .select_related('ano_letivo', 'escola')
            .annotate(
                qtd_alunos=Count(
                    'alunos_matriculados',
                    filter=Q(alunos_matriculados__ativo=True),
                )
            )
            .order_by('ano_letivo', 'nome')
        )


class TurmaCreateView(WebMixin, BootstrapFormMixin, SuccessMessageMixin, CreateView):
    model = Turma
    form_class = TurmaForm
    template_name = 'pages/turmas/form.html'
    success_url = reverse_lazy('web:turmas_list')
    success_message = 'Turma criada com sucesso.'
    active_menu = 'turmas'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Nova Turma'
        ctx['cancel_url'] = reverse_lazy('web:turmas_list')
        return ctx


class TurmaUpdateView(WebMixin, BootstrapFormMixin, SuccessMessageMixin, UpdateView):
    model = Turma
    form_class = TurmaForm
    template_name = 'pages/turmas/form.html'
    success_url = reverse_lazy('web:turmas_list')
    success_message = 'Turma atualizada com sucesso.'
    active_menu = 'turmas'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Editar Turma — {self.object}'
        ctx['cancel_url'] = reverse_lazy('web:turmas_list')
        return ctx
