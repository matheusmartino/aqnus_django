"""
Management command para popular o banco com dados de grade horaria da Etapa 5.

Uso:
    python manage.py seed_grade

Pre-requisito:
    Os dados das Etapas 1 e 2 devem existir:
    - python manage.py seed_data (Etapa 1)
    - python manage.py seed_academic (Etapa 2)

Escopo (Etapa 5 — grade horaria):
    - Horarios padrao (6 horarios matutino, 5 vespertino)
    - 1 Grade horaria completa para a turma 5o Ano A
    - Itens da grade (aulas) distribuidos sem conflitos

Caracteristicas:
    - Idempotente: usa get_or_create, pode rodar varias vezes sem duplicar
    - Atomico: roda dentro de transaction.atomic
    - NAO altera dados das Etapas anteriores

IMPORTANTE:
    - NAO cria chamada, frequencia, notas, diario (fora do escopo)
"""

from datetime import time

from django.core.management.base import BaseCommand
from django.db import transaction

from academic.models import (
    AnoLetivo,
    Disciplina,
    Turma,
    ProfessorDisciplina,
    Horario,
    GradeHoraria,
    GradeItem,
    DiaSemana,
)


# ─────────────────────────────────────────────────────────────
# Dados ficticios — Horarios
# ─────────────────────────────────────────────────────────────
# Horarios padrao do turno matutino (6 aulas) e vespertino (5 aulas).
# Cada horario tem 50 minutos com intervalos de 10 minutos.

HORARIOS = [
    # Matutino (07:30 - 12:30)
    {'ordem': 1, 'hora_inicio': time(7, 30), 'hora_fim': time(8, 20), 'turno': 'M'},
    {'ordem': 2, 'hora_inicio': time(8, 30), 'hora_fim': time(9, 20), 'turno': 'M'},
    {'ordem': 3, 'hora_inicio': time(9, 30), 'hora_fim': time(10, 20), 'turno': 'M'},
    {'ordem': 4, 'hora_inicio': time(10, 30), 'hora_fim': time(11, 20), 'turno': 'M'},
    {'ordem': 5, 'hora_inicio': time(11, 30), 'hora_fim': time(12, 20), 'turno': 'M'},
    {'ordem': 6, 'hora_inicio': time(12, 30), 'hora_fim': time(13, 20), 'turno': 'M'},
    # Vespertino (13:30 - 17:30)
    {'ordem': 1, 'hora_inicio': time(13, 30), 'hora_fim': time(14, 20), 'turno': 'V'},
    {'ordem': 2, 'hora_inicio': time(14, 30), 'hora_fim': time(15, 20), 'turno': 'V'},
    {'ordem': 3, 'hora_inicio': time(15, 30), 'hora_fim': time(16, 20), 'turno': 'V'},
    {'ordem': 4, 'hora_inicio': time(16, 30), 'hora_fim': time(17, 20), 'turno': 'V'},
    {'ordem': 5, 'hora_inicio': time(17, 30), 'hora_fim': time(18, 20), 'turno': 'V'},
]


# ─────────────────────────────────────────────────────────────
# Grade de exemplo — 5o Ano A (turno matutino)
# ─────────────────────────────────────────────────────────────
# Organizada para evitar conflitos:
# - Cada professor tem no maximo 1 aula por horario
# - Disciplinas distribuidas de forma equilibrada
#
# Legenda de professores (CPF do seed_data -> disciplinas habilitadas):
#   Roberto (MAT01, CIE01)
#   Fernanda (POR01, HIS01)
#   Marcos (GEO01, EDF01)

GRADE_5A = {
    # Segunda: MAT, POR, HIS, GEO, CIE, EDF
    DiaSemana.SEGUNDA: ['MAT01', 'POR01', 'HIS01', 'GEO01', 'CIE01', 'EDF01'],
    # Terca: POR, MAT, GEO, HIS, EDF, CIE
    DiaSemana.TERCA: ['POR01', 'MAT01', 'GEO01', 'HIS01', 'EDF01', 'CIE01'],
    # Quarta: MAT, HIS, POR, CIE, GEO, EDF
    DiaSemana.QUARTA: ['MAT01', 'HIS01', 'POR01', 'CIE01', 'GEO01', 'EDF01'],
    # Quinta: GEO, POR, MAT, EDF, HIS, CIE
    DiaSemana.QUINTA: ['GEO01', 'POR01', 'MAT01', 'EDF01', 'HIS01', 'CIE01'],
    # Sexta: POR, CIE, GEO, MAT, EDF, HIS
    DiaSemana.SEXTA: ['POR01', 'CIE01', 'GEO01', 'MAT01', 'EDF01', 'HIS01'],
}


class Command(BaseCommand):
    help = (
        'Popula o banco com dados de grade horaria da Etapa 5 '
        '(horarios, grade horaria, aulas). '
        'Idempotente — pode rodar varias vezes sem duplicar dados. '
        'Requer: seed_data (Etapa 1) e seed_academic (Etapa 2).'
    )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Populando dados de grade horaria da Etapa 5...\n')

        # Valida pre-requisitos
        if not self._validar_prerequisitos():
            return

        horarios = self._criar_horarios()
        grade = self._criar_grade_5a()
        if grade:
            self._criar_itens_grade(grade, horarios)

        self._imprimir_resumo()

    # ── Validacao ──────────────────────────────────────────

    def _validar_prerequisitos(self):
        """Verifica se os dados das Etapas 1 e 2 existem."""
        erros = []

        if AnoLetivo.objects.count() == 0:
            erros.append('Nenhum ano letivo encontrado.')

        if Turma.objects.count() == 0:
            erros.append('Nenhuma turma encontrada.')

        if ProfessorDisciplina.objects.count() == 0:
            erros.append('Nenhum vinculo professor-disciplina encontrado.')

        if erros:
            self.stderr.write(self.style.ERROR(
                'Dados das Etapas anteriores nao encontrados. '
                'Execute primeiro:\n'
                '  python manage.py seed_data\n'
                '  python manage.py seed_academic'
            ))
            for erro in erros:
                self.stderr.write(self.style.ERROR(f'  - {erro}'))
            return False
        return True

    # ── Horarios ─────────────────────────────────────────

    def _criar_horarios(self):
        self.stdout.write('--- Horarios ---')
        horarios = {}

        for data in HORARIOS:
            horario, created = Horario.objects.get_or_create(
                turno=data['turno'],
                ordem=data['ordem'],
                defaults={
                    'hora_inicio': data['hora_inicio'],
                    'hora_fim': data['hora_fim'],
                },
            )
            key = (data['turno'], data['ordem'])
            horarios[key] = horario

            turno_display = horario.get_turno_display()
            status = self.style.SUCCESS('criado') if created else 'ja existia'
            self.stdout.write(
                f'  {horario.ordem}o horario {turno_display} '
                f'({data["hora_inicio"].strftime("%H:%M")} - '
                f'{data["hora_fim"].strftime("%H:%M")}) — {status}'
            )

        return horarios

    # ── Grade Horaria ────────────────────────────────────

    def _criar_grade_5a(self):
        self.stdout.write('\n--- Grade Horaria ---')

        ano_letivo = AnoLetivo.objects.filter(nome='2025').first()
        if not ano_letivo:
            self.stderr.write(self.style.ERROR(
                '  Ano letivo 2025 nao encontrado.'
            ))
            return None

        turma = Turma.objects.filter(
            nome='5o Ano A',
            ano_letivo=ano_letivo,
        ).first()
        if not turma:
            self.stderr.write(self.style.ERROR(
                '  Turma 5o Ano A nao encontrada.'
            ))
            return None

        grade, created = GradeHoraria.objects.get_or_create(
            turma=turma,
            ano_letivo=ano_letivo,
            defaults={
                'ativa': True,
                'observacao': 'Grade criada pelo seed_grade.',
            },
        )

        status = self.style.SUCCESS('criada') if created else 'ja existia'
        self.stdout.write(f'  Grade {turma} — {ano_letivo} — {status}')

        return grade

    # ── Itens da Grade ───────────────────────────────────

    def _criar_itens_grade(self, grade, horarios):
        self.stdout.write('\n--- Itens da Grade (Aulas) ---')

        ano_letivo = grade.ano_letivo

        # Mapa de disciplina -> professor habilitado
        vinculos = ProfessorDisciplina.objects.filter(
            ano_letivo=ano_letivo
        ).select_related('professor', 'disciplina')

        disciplina_professor = {}
        for v in vinculos:
            disciplina_professor[v.disciplina.codigo] = v.professor

        # Mapa de codigo -> disciplina
        disciplinas = {
            d.codigo: d
            for d in Disciplina.objects.filter(ativa=True)
        }

        # Cria itens
        for dia, codigos in GRADE_5A.items():
            for ordem, codigo in enumerate(codigos, start=1):
                horario = horarios.get(('M', ordem))  # Turno matutino
                if not horario:
                    continue

                disciplina = disciplinas.get(codigo)
                if not disciplina:
                    self.stderr.write(self.style.WARNING(
                        f'  Disciplina {codigo} nao encontrada, pulando.'
                    ))
                    continue

                professor = disciplina_professor.get(codigo)
                if not professor:
                    self.stderr.write(self.style.WARNING(
                        f'  Professor para {codigo} nao encontrado, pulando.'
                    ))
                    continue

                item, created = GradeItem.objects.get_or_create(
                    grade_horaria=grade,
                    dia_semana=dia,
                    horario=horario,
                    defaults={
                        'disciplina': disciplina,
                        'professor': professor,
                    },
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'  {dia} {ordem}o h — {disciplina.nome} ({professor})'
                    ))
                else:
                    self.stdout.write(
                        f'  {dia} {ordem}o h — {disciplina.nome} — ja existia'
                    )

    # ── Resumo ─────────────────────────────────────────────

    def _imprimir_resumo(self):
        self.stdout.write('\n--- Resumo Etapa 5 ---')
        self.stdout.write(f'  Horarios:       {Horario.objects.count()}')
        self.stdout.write(f'  Grades:         {GradeHoraria.objects.count()}')
        self.stdout.write(f'  Itens (aulas):  {GradeItem.objects.count()}')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Seed grade concluido com sucesso.'))
