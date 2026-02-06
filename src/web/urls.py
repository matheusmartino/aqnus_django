from django.urls import path

from . import views

app_name = 'web'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Alunos
    path('alunos/', views.AlunoListView.as_view(), name='alunos_list'),
    path('alunos/novo/', views.AlunoCreateView.as_view(), name='aluno_create'),
    path('alunos/<int:pk>/editar/', views.AlunoUpdateView.as_view(), name='aluno_edit'),

    # Turmas
    path('turmas/', views.TurmaListView.as_view(), name='turmas_list'),
    path('turmas/nova/', views.TurmaCreateView.as_view(), name='turma_create'),
    path('turmas/<int:pk>/editar/', views.TurmaUpdateView.as_view(), name='turma_edit'),

    # Professores
    path('professores/', views.ProfessorListView.as_view(), name='professores_list'),
    path('professores/novo/', views.ProfessorCreateView.as_view(), name='professor_create'),
    path('professores/<int:pk>/editar/', views.ProfessorUpdateView.as_view(), name='professor_edit'),

    # Biblioteca (Obras)
    path('biblioteca/', views.ObraListView.as_view(), name='biblioteca_list'),
    path('biblioteca/nova/', views.ObraCreateView.as_view(), name='obra_create'),
    path('biblioteca/<int:pk>/editar/', views.ObraUpdateView.as_view(), name='obra_edit'),
]
