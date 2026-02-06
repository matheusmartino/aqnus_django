"""
web.views.dashboard_views

View do dashboard principal.
"""

from django.shortcuts import render

from people.models import Aluno, Professor
from academic.models import Turma
from library.models import Emprestimo


def dashboard(request):
    total_alunos = Aluno.objects.filter(situacao='ativo').count()
    total_turmas = Turma.objects.filter(ativa=True).count()
    total_professores = Professor.objects.filter(ativo=True).count()
    total_emprestimos = Emprestimo.objects.filter(
        status__in=[Emprestimo.Status.ATIVO, Emprestimo.Status.ATRASADO],
    ).count()
    emprestimos_atrasados = Emprestimo.objects.filter(
        status=Emprestimo.Status.ATRASADO,
    ).select_related('exemplar__obra', 'aluno__pessoa')

    return render(request, 'pages/dashboard.html', {
        'active_menu': 'dashboard',
        'total_alunos': total_alunos,
        'total_turmas': total_turmas,
        'total_professores': total_professores,
        'total_emprestimos': total_emprestimos,
        'emprestimos_atrasados': emprestimos_atrasados,
    })
