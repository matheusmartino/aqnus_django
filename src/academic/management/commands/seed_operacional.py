"""
Management command para popular o banco com dados operacionais da Etapa 3.

Uso:
    python manage.py seed_operacional

Pre-requisito:
    Os dados das Etapas 1 e 2 devem existir:
        python manage.py seed_data
        python manage.py seed_academic

Escopo (Etapa 3 — operacao escolar e filiacao):
    - Matriculas formais para alunos existentes (via MatriculaService)
    - Um aluno transferido de turma (com historico)
    - Um aluno com matricula encerrada (conclusao)
    - 4 Responsaveis (pais/maes) vinculados a Pessoas
    - 2 alunos irmaos compartilhando os mesmos responsaveis
    - Historico de movimentacoes gerado automaticamente pelo service

Caracteristicas:
    - Idempotente: verifica existencia antes de criar
    - Atomico: roda dentro de transaction.atomic
    - NAO altera dados das Etapas 1 e 2
    - Usa MatriculaService para garantir consistencia
"""

from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Escola
from people.models import (
    Pessoa,
    Aluno,
    Responsavel,
    AlunoResponsavel,
)
from academic.models import (
    AnoLetivo,
    Turma,
    Matricula,
    MovimentacaoAluno,
)
from academic.services import MatriculaService


# ─────────────────────────────────────────────────────────────
# Dados ficticios — Responsaveis (Pessoas novas)
# ─────────────────────────────────────────────────────────────
# Pais/maes dos alunos existentes. Serao vinculados como Responsavel.

RESPONSAVEIS = [
    {
        'pessoa': {
            'nome': 'Carlos Alberto Santos',
            'cpf': '321.654.987-01',
            'data_nascimento': date(1978, 5, 20),
            'telefone': '(11) 98765-0001',
            'email': 'carlos.santos@email.com',
            'endereco': 'Rua A, 10 - Centro, Sao Paulo/SP',
        },
        'tipo': 'pai',
    },
    {
        'pessoa': {
            'nome': 'Ana Paula Pereira',
            'cpf': '654.321.098-12',
            'data_nascimento': date(1982, 9, 10),
            'telefone': '(11) 98765-0002',
            'email': 'ana.pereira@email.com',
            'endereco': 'Rua A, 10 - Centro, Sao Paulo/SP',
        },
        'tipo': 'mae',
    },
    {
        'pessoa': {
            'nome': 'Roberto Ferreira Lima',
            'cpf': '147.258.369-03',
            'data_nascimento': date(1980, 2, 14),
            'telefone': '(11) 98765-0003',
            'email': 'roberto.lima@email.com',
            'endereco': 'Rua B, 20 - Vila Nova, Sao Paulo/SP',
        },
        'tipo': 'pai',
    },
    {
        'pessoa': {
            'nome': 'Maria Clara Ferreira',
            'cpf': '258.369.147-24',
            'data_nascimento': date(1984, 11, 30),
            'telefone': '(11) 98765-0004',
            'email': 'maria.ferreira@email.com',
            'endereco': 'Rua B, 20 - Vila Nova, Sao Paulo/SP',
        },
        'tipo': 'mae',
    },
]


# ─────────────────────────────────────────────────────────────
# Vinculos Aluno → Responsavel
# ─────────────────────────────────────────────────────────────
# Lucas e Julia sao irmaos — compartilham os mesmos responsaveis
# (Carlos = pai, Ana Paula = mae de ambos).
# Pedro tem Roberto e Maria Clara como pais.

VINCULOS_RESPONSAVEL = [
    # Lucas Pereira Santos ← Carlos (pai) + Ana Paula (mae)
    {
        'aluno_matricula': '2025001',
        'responsavel_cpf': '321.654.987-01',
        'tipo_vinculo': 'pai',
        'responsavel_principal': True,
        'autorizado_retirar': True,
    },
    {
        'aluno_matricula': '2025001',
        'responsavel_cpf': '654.321.098-12',
        'tipo_vinculo': 'mae',
        'responsavel_principal': False,
        'autorizado_retirar': True,
    },
    # Julia Ferreira Lima ← Carlos (pai) + Ana Paula (mae) — irma do Lucas
    {
        'aluno_matricula': '2025002',
        'responsavel_cpf': '321.654.987-01',
        'tipo_vinculo': 'pai',
        'responsavel_principal': False,
        'autorizado_retirar': True,
    },
    {
        'aluno_matricula': '2025002',
        'responsavel_cpf': '654.321.098-12',
        'tipo_vinculo': 'mae',
        'responsavel_principal': True,
        'autorizado_retirar': True,
    },
    # Pedro Henrique Costa ← Roberto (pai) + Maria Clara (mae)
    {
        'aluno_matricula': '2025003',
        'responsavel_cpf': '147.258.369-03',
        'tipo_vinculo': 'pai',
        'responsavel_principal': True,
        'autorizado_retirar': True,
    },
    {
        'aluno_matricula': '2025003',
        'responsavel_cpf': '258.369.147-24',
        'tipo_vinculo': 'mae',
        'responsavel_principal': False,
        'autorizado_retirar': True,
    },
]


class Command(BaseCommand):
    help = (
        'Popula o banco com dados operacionais da Etapa 3 '
        '(matriculas formais, transferencias, responsaveis, filiacao). '
        'Idempotente — pode rodar varias vezes sem duplicar dados. '
        'Requer: seed_data (Etapa 1) e seed_academic (Etapa 2).'
    )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Populando dados operacionais da Etapa 3...\n')

        if not self._validar_prerequisitos():
            return

        self._criar_matriculas_formais()
        self._simular_transferencia()
        self._simular_encerramento()
        self._criar_responsaveis()
        self._criar_vinculos_responsavel()
        self._imprimir_resumo()

    # ── Validacao ──────────────────────────────────────────

    def _validar_prerequisitos(self):
        """Verifica se os dados das Etapas 1 e 2 existem."""
        erros = []
        if Escola.objects.count() == 0:
            erros.append('Nenhuma escola encontrada.')
        if Aluno.objects.count() == 0:
            erros.append('Nenhum aluno encontrado.')
        if AnoLetivo.objects.count() == 0:
            erros.append('Nenhum ano letivo encontrado.')
        if Turma.objects.count() == 0:
            erros.append('Nenhuma turma encontrada.')

        if erros:
            self.stderr.write(self.style.ERROR(
                'Dados das Etapas 1 e 2 nao encontrados. Execute primeiro:\n'
                '  python manage.py seed_data\n'
                '  python manage.py seed_academic'
            ))
            for erro in erros:
                self.stderr.write(self.style.ERROR(f'  - {erro}'))
            return False
        return True

    # ── Matriculas formais ─────────────────────────────────

    def _criar_matriculas_formais(self):
        """Cria matriculas formais (Etapa 3) para alunos ja existentes."""
        self.stdout.write('--- Matriculas formais ---')

        ano_letivo = AnoLetivo.objects.filter(nome='2025').first()
        if not ano_letivo:
            self.stderr.write(self.style.WARNING(
                '  Ano letivo 2025 nao encontrado, pulando matriculas.'
            ))
            return

        # Matriculas para cada aluno com AlunoTurma ativo
        from academic.models import AlunoTurma
        vinculos = AlunoTurma.objects.filter(
            turma__ano_letivo=ano_letivo,
            ativo=True,
        ).select_related('aluno', 'turma')

        for vinculo in vinculos:
            # Pula se ja tem matricula para este aluno/ano
            if Matricula.objects.filter(
                aluno=vinculo.aluno,
                ano_letivo=ano_letivo,
            ).exists():
                self.stdout.write(
                    f'  {vinculo.aluno} -> {vinculo.turma} — ja tem matricula'
                )
                continue

            try:
                MatriculaService.matricular_aluno(
                    aluno=vinculo.aluno,
                    turma=vinculo.turma,
                    ano_letivo=ano_letivo,
                    data_matricula=ano_letivo.data_inicio,
                    tipo=Matricula.Tipo.INICIAL,
                )
                self.stdout.write(self.style.SUCCESS(
                    f'  {vinculo.aluno} -> {vinculo.turma} — matriculado'
                ))
            except Exception as e:
                self.stderr.write(self.style.WARNING(
                    f'  {vinculo.aluno}: {e}'
                ))

    # ── Transferencia ──────────────────────────────────────

    def _simular_transferencia(self):
        """Simula transferencia de Isabela do 5o Ano B para 5o Ano A."""
        self.stdout.write('\n--- Transferencia ---')

        aluno = Aluno.objects.filter(matricula='2024010').first()
        if not aluno:
            self.stdout.write('  Aluno 2024010 nao encontrado, pulando.')
            return

        ano_letivo = AnoLetivo.objects.filter(nome='2025').first()
        if not ano_letivo:
            return

        turma_destino = Turma.objects.filter(
            nome='5o Ano A', ano_letivo=ano_letivo,
        ).first()
        if not turma_destino:
            return

        # Verifica se a transferencia ja foi feita
        if Matricula.objects.filter(
            aluno=aluno,
            ano_letivo=ano_letivo,
            tipo=Matricula.Tipo.TRANSFERENCIA,
        ).exists():
            self.stdout.write(f'  {aluno} — ja transferido')
            return

        matricula_atual = Matricula.objects.filter(
            aluno=aluno,
            ano_letivo=ano_letivo,
            status=Matricula.Status.ATIVA,
        ).first()

        if not matricula_atual:
            self.stdout.write(f'  {aluno} — sem matricula ativa para transferir')
            return

        try:
            MatriculaService.transferir_aluno(
                matricula_atual=matricula_atual,
                nova_turma=turma_destino,
                data=date(2025, 4, 15),
                observacao='Remanejamento por solicitacao da coordenacao.',
            )
            self.stdout.write(self.style.SUCCESS(
                f'  {aluno} — transferido para {turma_destino}'
            ))
        except Exception as e:
            self.stderr.write(self.style.WARNING(f'  {aluno}: {e}'))

    # ── Encerramento ───────────────────────────────────────

    def _simular_encerramento(self):
        """Simula encerramento de matricula de Gabriel (conclusao)."""
        self.stdout.write('\n--- Encerramento ---')

        aluno = Aluno.objects.filter(matricula='2025004').first()
        if not aluno:
            self.stdout.write('  Aluno 2025004 nao encontrado, pulando.')
            return

        ano_letivo = AnoLetivo.objects.filter(nome='2025').first()
        if not ano_letivo:
            return

        # Verifica se ja encerrou
        if Matricula.objects.filter(
            aluno=aluno,
            ano_letivo=ano_letivo,
            status=Matricula.Status.ENCERRADA,
        ).exists():
            self.stdout.write(f'  {aluno} — ja encerrado')
            return

        matricula = Matricula.objects.filter(
            aluno=aluno,
            ano_letivo=ano_letivo,
            status=Matricula.Status.ATIVA,
        ).first()

        if not matricula:
            self.stdout.write(f'  {aluno} — sem matricula ativa para encerrar')
            return

        try:
            MatriculaService.encerrar_matricula(
                matricula=matricula,
                data=date(2025, 12, 12),
                motivo='Conclusao do ano letivo.',
            )
            self.stdout.write(self.style.SUCCESS(
                f'  {aluno} — matricula encerrada'
            ))

            # Atualiza situacao do aluno para formado
            aluno.situacao = 'formado'
            aluno.save(update_fields=['situacao', 'atualizado_em'])
        except Exception as e:
            self.stderr.write(self.style.WARNING(f'  {aluno}: {e}'))

    # ── Responsaveis ───────────────────────────────────────

    def _criar_responsaveis(self):
        """Cria pessoas e perfis de responsavel."""
        self.stdout.write('\n--- Responsaveis ---')

        for item in RESPONSAVEIS:
            pessoa_data = item['pessoa']
            pessoa, p_created = Pessoa.objects.get_or_create(
                cpf=pessoa_data['cpf'],
                defaults=pessoa_data,
            )
            p_status = self.style.SUCCESS('criada') if p_created else 'ja existia'
            self.stdout.write(f'  Pessoa: {pessoa.nome} — {p_status}')

            _, r_created = Responsavel.objects.get_or_create(
                pessoa=pessoa,
                defaults={'tipo': item['tipo']},
            )
            if r_created:
                self.stdout.write(self.style.SUCCESS(
                    f'    -> Responsavel ({item["tipo"]})'
                ))

    # ── Vinculos Aluno-Responsavel ─────────────────────────

    def _criar_vinculos_responsavel(self):
        """Vincula alunos a responsaveis (filiacao)."""
        self.stdout.write('\n--- Vinculos Aluno-Responsavel ---')

        for v in VINCULOS_RESPONSAVEL:
            aluno = Aluno.objects.filter(
                matricula=v['aluno_matricula'],
            ).first()
            responsavel = Responsavel.objects.filter(
                pessoa__cpf=v['responsavel_cpf'],
            ).first()

            if not aluno or not responsavel:
                self.stdout.write(self.style.WARNING(
                    f'  Aluno {v["aluno_matricula"]} ou responsavel '
                    f'{v["responsavel_cpf"]} nao encontrado, pulando.'
                ))
                continue

            _, created = AlunoResponsavel.objects.get_or_create(
                aluno=aluno,
                responsavel=responsavel,
                defaults={
                    'tipo_vinculo': v['tipo_vinculo'],
                    'responsavel_principal': v['responsavel_principal'],
                    'autorizado_retirar_aluno': v['autorizado_retirar'],
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'  {aluno} <- {responsavel} ({v["tipo_vinculo"]})'
                ))
            else:
                self.stdout.write(
                    f'  {aluno} <- {responsavel} — ja existia'
                )

    # ── Resumo ─────────────────────────────────────────────

    def _imprimir_resumo(self):
        self.stdout.write('\n--- Resumo Etapa 3 ---')
        self.stdout.write(
            f'  Matriculas:        {Matricula.objects.count()}'
        )
        self.stdout.write(
            f'  Movimentacoes:     {MovimentacaoAluno.objects.count()}'
        )
        self.stdout.write(
            f'  Responsaveis:      {Responsavel.objects.count()}'
        )
        self.stdout.write(
            f'  Aluno-Responsavel: {AlunoResponsavel.objects.count()}'
        )
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            'Seed operacional concluido com sucesso.'
        ))
