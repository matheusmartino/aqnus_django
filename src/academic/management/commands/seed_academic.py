"""
Management command para popular o banco com dados academicos da Etapa 2.

Uso:
    python manage.py seed_academic

Pre-requisito:
    Os dados da Etapa 1 devem existir (python manage.py seed_data).
    Este comando depende da Escola, Professores e Alunos criados pelo seed_data.

Escopo (apenas Etapa 2 — estrutura academica):
    - 1 Ano Letivo (2025, ativo)
    - 6 Disciplinas
    - 2 Turmas vinculadas a escola existente
    - Professores vinculados a disciplinas (ProfessorDisciplina)
    - Alunos matriculados em turmas (AlunoTurma)

Caracteristicas:
    - Idempotente: usa get_or_create, pode rodar varias vezes sem duplicar
    - Atomico: roda dentro de transaction.atomic
    - NAO altera dados da Etapa 1

IMPORTANTE:
    - NAO cria notas, frequencia, horarios (Etapa 3+)
"""

from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Escola
from people.models import Aluno, Professor
from academic.models import (
    AnoLetivo,
    Disciplina,
    Turma,
    ProfessorDisciplina,
    AlunoTurma,
)


# ─────────────────────────────────────────────────────────────
# Dados ficticios — Ano Letivo
# ─────────────────────────────────────────────────────────────

ANO_LETIVO = {
    'nome': '2025',
    'data_inicio': date(2025, 2, 3),
    'data_fim': date(2025, 12, 12),
    'ativo': True,
}


# ─────────────────────────────────────────────────────────────
# Dados ficticios — Disciplinas
# ─────────────────────────────────────────────────────────────
# Disciplinas tipicas do ensino fundamental.
# Codigo segue padrao: sigla + numero sequencial.

DISCIPLINAS = [
    {'nome': 'Matematica',          'codigo': 'MAT01', 'carga_horaria': 160},
    {'nome': 'Lingua Portuguesa',   'codigo': 'POR01', 'carga_horaria': 160},
    {'nome': 'Historia',            'codigo': 'HIS01', 'carga_horaria': 80},
    {'nome': 'Geografia',           'codigo': 'GEO01', 'carga_horaria': 80},
    {'nome': 'Ciencias',            'codigo': 'CIE01', 'carga_horaria': 80},
    {'nome': 'Educacao Fisica',     'codigo': 'EDF01', 'carga_horaria': 80},
]


# ─────────────────────────────────────────────────────────────
# Dados ficticios — Turmas
# ─────────────────────────────────────────────────────────────
# Vinculadas ao ano letivo 2025 e a escola do seed_data.

TURMAS = [
    {'nome': '5o Ano A'},
    {'nome': '5o Ano B'},
]


# ─────────────────────────────────────────────────────────────
# Vinculos Professor -> Disciplina
# ─────────────────────────────────────────────────────────────
# Chave: CPF do professor (do seed_data)
# Valor: lista de codigos de disciplina

VINCULOS_PROFESSOR = {
    # Roberto Carlos Mendes (Matematica - USP)
    '234.567.890-92': ['MAT01', 'CIE01'],
    # Fernanda Souza Barbosa (Lingua Portuguesa - PUC-SP)
    '345.678.901-75': ['POR01', 'HIS01'],
    # Marcos Antonio da Silva (Historia - UNICAMP)
    '456.789.012-49': ['GEO01', 'EDF01'],
}


# ─────────────────────────────────────────────────────────────
# Matriculas Aluno -> Turma
# ─────────────────────────────────────────────────────────────
# Chave: nome da turma
# Valor: lista de matriculas de alunos (do seed_data)

MATRICULAS_TURMA = {
    '5o Ano A': ['2025001', '2025002', '2025003'],
    '5o Ano B': ['2024010', '2025004'],
}


class Command(BaseCommand):
    help = (
        'Popula o banco com dados academicos da Etapa 2 '
        '(ano letivo, disciplinas, turmas, vinculos professor-disciplina, '
        'matriculas aluno-turma). '
        'Idempotente — pode rodar varias vezes sem duplicar dados. '
        'Requer: python manage.py seed_data (Etapa 1).'
    )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Populando dados academicos da Etapa 2...\n')

        # Valida pre-requisitos da Etapa 1
        if not self._validar_prerequisitos():
            return

        ano_letivo = self._criar_ano_letivo()
        self._criar_disciplinas()
        escola = Escola.objects.first()
        turmas = self._criar_turmas(ano_letivo, escola)
        self._criar_vinculos_professor(ano_letivo)
        self._criar_matriculas_aluno(turmas)
        self._imprimir_resumo()

    # ── Validacao ──────────────────────────────────────────

    def _validar_prerequisitos(self):
        """Verifica se os dados da Etapa 1 existem."""
        erros = []
        if Escola.objects.count() == 0:
            erros.append('Nenhuma escola encontrada.')
        if Professor.objects.count() == 0:
            erros.append('Nenhum professor encontrado.')
        if Aluno.objects.count() == 0:
            erros.append('Nenhum aluno encontrado.')

        if erros:
            self.stderr.write(self.style.ERROR(
                'Dados da Etapa 1 nao encontrados. '
                'Execute primeiro: python manage.py seed_data'
            ))
            for erro in erros:
                self.stderr.write(self.style.ERROR(f'  - {erro}'))
            return False
        return True

    # ── Ano Letivo ─────────────────────────────────────────

    def _criar_ano_letivo(self):
        self.stdout.write('--- Ano Letivo ---')
        ano, created = AnoLetivo.objects.get_or_create(
            nome=ANO_LETIVO['nome'],
            defaults=ANO_LETIVO,
        )
        status = self.style.SUCCESS('criado') if created else 'ja existia'
        self.stdout.write(f'  {ano.nome} ({ano.data_inicio} a {ano.data_fim}) — {status}')
        return ano

    # ── Disciplinas ────────────────────────────────────────

    def _criar_disciplinas(self):
        self.stdout.write('\n--- Disciplinas ---')
        for data in DISCIPLINAS:
            disc, created = Disciplina.objects.get_or_create(
                codigo=data['codigo'],
                defaults=data,
            )
            status = self.style.SUCCESS('criada') if created else 'ja existia'
            self.stdout.write(f'  {disc.nome} ({disc.codigo}) — {status}')

    # ── Turmas ─────────────────────────────────────────────

    def _criar_turmas(self, ano_letivo, escola):
        self.stdout.write('\n--- Turmas ---')
        turmas = {}
        for data in TURMAS:
            turma, created = Turma.objects.get_or_create(
                nome=data['nome'],
                ano_letivo=ano_letivo,
                escola=escola,
            )
            turmas[turma.nome] = turma
            status = self.style.SUCCESS('criada') if created else 'ja existia'
            self.stdout.write(f'  {turma.nome} — {escola.nome} — {status}')
        return turmas

    # ── Professor-Disciplina ───────────────────────────────

    def _criar_vinculos_professor(self, ano_letivo):
        self.stdout.write('\n--- Professor-Disciplina ---')
        for cpf, codigos in VINCULOS_PROFESSOR.items():
            professor = Professor.objects.filter(pessoa__cpf=cpf).first()
            if not professor:
                self.stderr.write(self.style.WARNING(
                    f'  Professor com CPF {cpf} nao encontrado, pulando.'
                ))
                continue

            for codigo in codigos:
                disciplina = Disciplina.objects.filter(codigo=codigo).first()
                if not disciplina:
                    continue

                _, created = ProfessorDisciplina.objects.get_or_create(
                    professor=professor,
                    disciplina=disciplina,
                    ano_letivo=ano_letivo,
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'  {professor} -> {disciplina.nome}'
                    ))
                else:
                    self.stdout.write(
                        f'  {professor} -> {disciplina.nome} — ja existia'
                    )

    # ── Aluno-Turma ────────────────────────────────────────

    def _criar_matriculas_aluno(self, turmas):
        self.stdout.write('\n--- Aluno-Turma ---')
        for nome_turma, matriculas in MATRICULAS_TURMA.items():
            turma = turmas.get(nome_turma)
            if not turma:
                continue

            for matricula in matriculas:
                aluno = Aluno.objects.filter(matricula=matricula).first()
                if not aluno:
                    self.stderr.write(self.style.WARNING(
                        f'  Aluno matricula {matricula} nao encontrado, pulando.'
                    ))
                    continue

                _, created = AlunoTurma.objects.get_or_create(
                    aluno=aluno,
                    turma=turma,
                    defaults={
                        'data_matricula': turma.ano_letivo.data_inicio,
                    },
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'  {aluno} -> {turma.nome}'
                    ))
                else:
                    self.stdout.write(
                        f'  {aluno} -> {turma.nome} — ja existia'
                    )

    # ── Resumo ─────────────────────────────────────────────

    def _imprimir_resumo(self):
        self.stdout.write('\n--- Resumo Etapa 2 ---')
        self.stdout.write(f'  Anos Letivos:          {AnoLetivo.objects.count()}')
        self.stdout.write(f'  Disciplinas:           {Disciplina.objects.count()}')
        self.stdout.write(f'  Turmas:                {Turma.objects.count()}')
        self.stdout.write(f'  Professor-Disciplina:  {ProfessorDisciplina.objects.count()}')
        self.stdout.write(f'  Aluno-Turma:           {AlunoTurma.objects.count()}')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Seed academico concluido com sucesso.'))
