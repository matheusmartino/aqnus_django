"""
web.views.biblioteca_views

Views CRUD da biblioteca (obras).
"""

from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from library.forms import ObraForm
from library.models import Obra

from .mixins import BootstrapFormMixin, WebMixin


class ObraListView(WebMixin, ListView):
    model = Obra
    template_name = 'pages/biblioteca/list.html'
    context_object_name = 'obras'
    active_menu = 'biblioteca'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['create_url'] = reverse_lazy('web:obra_create')
        return ctx

    def get_queryset(self):
        return (
            Obra.objects
            .filter(ativa=True)
            .select_related('editora', 'assunto')
            .prefetch_related('autores')
            .annotate(
                exemplares_disponiveis=Count(
                    'exemplares',
                    filter=Q(exemplares__situacao='disponivel', exemplares__ativo=True),
                ),
                emprestimos_ativos=Count(
                    'exemplares__emprestimos',
                    filter=Q(
                        exemplares__emprestimos__status__in=['ativo', 'atrasado'],
                    ),
                ),
            )
            .order_by('titulo')
        )


class ObraCreateView(WebMixin, BootstrapFormMixin, SuccessMessageMixin, CreateView):
    model = Obra
    form_class = ObraForm
    template_name = 'pages/biblioteca/form.html'
    success_url = reverse_lazy('web:biblioteca_list')
    success_message = 'Obra criada com sucesso.'
    active_menu = 'biblioteca'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Nova Obra'
        ctx['cancel_url'] = reverse_lazy('web:biblioteca_list')
        return ctx


class ObraUpdateView(WebMixin, BootstrapFormMixin, SuccessMessageMixin, UpdateView):
    model = Obra
    form_class = ObraForm
    template_name = 'pages/biblioteca/form.html'
    success_url = reverse_lazy('web:biblioteca_list')
    success_message = 'Obra atualizada com sucesso.'
    active_menu = 'biblioteca'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Editar Obra — {self.object}'
        ctx['cancel_url'] = reverse_lazy('web:biblioteca_list')
        return ctx
