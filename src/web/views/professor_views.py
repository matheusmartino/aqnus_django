"""
web.views.professor_views

Views CRUD de professores.
"""

from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from people.forms import ProfessorForm
from people.models import Professor

from .mixins import BootstrapFormMixin, WebMixin


class ProfessorListView(WebMixin, ListView):
    model = Professor
    template_name = 'pages/professores/list.html'
    context_object_name = 'professores'
    active_menu = 'professores'

    def get_queryset(self):
        return Professor.objects.select_related('pessoa').all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['create_url'] = reverse_lazy('web:professor_create')
        return ctx


class ProfessorCreateView(WebMixin, BootstrapFormMixin, SuccessMessageMixin, CreateView):
    model = Professor
    form_class = ProfessorForm
    template_name = 'pages/professores/form.html'
    success_url = reverse_lazy('web:professores_list')
    success_message = 'Professor criado com sucesso.'
    active_menu = 'professores'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Novo Professor'
        ctx['cancel_url'] = reverse_lazy('web:professores_list')
        return ctx


class ProfessorUpdateView(WebMixin, BootstrapFormMixin, SuccessMessageMixin, UpdateView):
    model = Professor
    form_class = ProfessorForm
    template_name = 'pages/professores/form.html'
    success_url = reverse_lazy('web:professores_list')
    success_message = 'Professor atualizado com sucesso.'
    active_menu = 'professores'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Editar Professor — {self.object}'
        ctx['cancel_url'] = reverse_lazy('web:professores_list')
        return ctx
