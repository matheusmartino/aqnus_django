from .home_views import home
from .dashboard_views import dashboard
from .aluno_views import AlunoListView, AlunoCreateView, AlunoUpdateView
from .turma_views import TurmaListView, TurmaCreateView, TurmaUpdateView
from .professor_views import ProfessorListView, ProfessorCreateView, ProfessorUpdateView
from .biblioteca_views import ObraListView, ObraCreateView, ObraUpdateView

__all__ = [
    'home',
    'dashboard',
    'AlunoListView',
    'AlunoCreateView',
    'AlunoUpdateView',
    'TurmaListView',
    'TurmaCreateView',
    'TurmaUpdateView',
    'ProfessorListView',
    'ProfessorCreateView',
    'ProfessorUpdateView',
    'ObraListView',
    'ObraCreateView',
    'ObraUpdateView',
]
