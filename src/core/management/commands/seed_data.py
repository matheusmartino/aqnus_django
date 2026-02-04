"""
Management command para popular o banco com dados iniciais da Etapa 1.

Uso:
    python manage.py seed_data

Escopo (apenas Etapa 1 — cadastros fundamentais):
    - 1 Escola
    - 11 Pessoas (com dados completos)
    - 5 Alunos (vinculados a Pessoa)
    - 3 Professores (vinculados a Pessoa)
    - 2 Funcionarios (vinculados a Pessoa)
    - 1 Pessoa sem perfil (cadastro generico)

Caracteristicas:
    - Idempotente: usa get_or_create, pode rodar varias vezes sem duplicar
    - Atomico: roda dentro de transaction.atomic
    - Todos os dados sao ficticios (CPFs validos algoritmicamente, mas inventados)

IMPORTANTE:
    - NAO cria dados de Etapa 2+ (turmas, disciplinas, notas, etc.)
    - NAO cria usuarios do sistema (use: python manage.py create_test_users)
"""

from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Escola
from people.models import Pessoa, Aluno, Professor, Funcionario


# ─────────────────────────────────────────────────────────────
# Dados ficticios — Escola
# ─────────────────────────────────────────────────────────────
# Uma escola modelo para validacao da Etapa 1.
# CPFs abaixo passam no algoritmo de verificacao, mas sao inventados.

ESCOLA = {
    'nome': 'Escola Modelo AQNUS',
    'cnpj': '12.345.678/0001-90',
    'endereco': 'Rua das Palmeiras, 200 - Centro, Sao Paulo/SP',
    'telefone': '(11) 3456-7890',
    'email': 'contato@escolaaqnus.edu.br',
}


# ─────────────────────────────────────────────────────────────
# Dados ficticios — Pessoas e perfis
# ─────────────────────────────────────────────────────────────
# Cada entrada representa uma Pessoa com dados pessoais completos.
# O campo 'perfil' indica o tipo de vinculo a ser criado:
#   'aluno'       -> cria registro em Aluno
#   'professor'   -> cria registro em Professor
#   'funcionario' -> cria registro em Funcionario
#   None          -> apenas Pessoa (ex: responsavel, contato)

PESSOAS = [

    # ── Alunos (5) ──────────────────────────────────────────

    {
        'nome': 'Lucas Pereira Santos',
        'cpf': '123.456.789-09',          # CPF valido ficticio
        'data_nascimento': date(2010, 3, 15),
        'telefone': '(11) 91234-0001',
        'email': 'lucas.santos@email.com',
        'endereco': 'Rua A, 10 - Centro, Sao Paulo/SP',
        'perfil': 'aluno',
        'aluno': {
            'matricula': '2025001',
            'data_ingresso': date(2025, 2, 1),
            'situacao': 'ativo',
        },
    },
    {
        'nome': 'Julia Ferreira Lima',
        'cpf': '987.654.321-00',
        'data_nascimento': date(2011, 7, 22),
        'telefone': '(11) 91234-0002',
        'email': 'julia.lima@email.com',
        'endereco': 'Rua B, 20 - Vila Nova, Sao Paulo/SP',
        'perfil': 'aluno',
        'aluno': {
            'matricula': '2025002',
            'data_ingresso': date(2025, 2, 1),
            'situacao': 'ativo',
        },
    },
    {
        'nome': 'Pedro Henrique Costa',
        'cpf': '111.222.333-96',
        'data_nascimento': date(2009, 11, 5),
        'telefone': '(11) 91234-0003',
        'email': 'pedro.costa@email.com',
        'endereco': 'Rua C, 30 - Jardim Europa, Sao Paulo/SP',
        'perfil': 'aluno',
        'aluno': {
            'matricula': '2025003',
            'data_ingresso': date(2025, 2, 1),
            'situacao': 'ativo',
        },
    },
    {
        'nome': 'Isabela Rodrigues Almeida',
        'cpf': '444.555.666-19',
        'data_nascimento': date(2010, 1, 30),
        'telefone': '(11) 91234-0004',
        'email': 'isabela.almeida@email.com',
        'endereco': 'Rua D, 40 - Liberdade, Sao Paulo/SP',
        'perfil': 'aluno',
        'aluno': {
            'matricula': '2024010',
            'data_ingresso': date(2024, 2, 5),
            'situacao': 'ativo',
        },
    },
    {
        'nome': 'Gabriel Oliveira Souza',
        'cpf': '567.890.123-03',
        'data_nascimento': date(2011, 5, 8),
        'telefone': '(11) 91234-0005',
        'email': 'gabriel.souza@email.com',
        'endereco': 'Rua E, 50 - Mooca, Sao Paulo/SP',
        'perfil': 'aluno',
        'aluno': {
            'matricula': '2025004',
            'data_ingresso': date(2025, 2, 1),
            'situacao': 'ativo',
        },
    },

    # ── Professores (3) ────────────────────────────────────

    {
        'nome': 'Roberto Carlos Mendes',
        'cpf': '234.567.890-92',
        'data_nascimento': date(1980, 5, 10),
        'telefone': '(11) 92345-0001',
        'email': 'roberto.mendes@email.com',
        'endereco': 'Av. Paulista, 1000 - Bela Vista, Sao Paulo/SP',
        'perfil': 'professor',
        'professor': {
            'formacao': 'Licenciatura em Matematica - USP',
            'carga_horaria_max': 40,
        },
    },
    {
        'nome': 'Fernanda Souza Barbosa',
        'cpf': '345.678.901-75',
        'data_nascimento': date(1985, 9, 18),
        'telefone': '(11) 92345-0002',
        'email': 'fernanda.barbosa@email.com',
        'endereco': 'Rua Augusta, 200 - Consolacao, Sao Paulo/SP',
        'perfil': 'professor',
        'professor': {
            'formacao': 'Licenciatura em Lingua Portuguesa - PUC-SP',
            'carga_horaria_max': 30,
        },
    },
    {
        'nome': 'Marcos Antonio da Silva',
        'cpf': '456.789.012-49',
        'data_nascimento': date(1978, 12, 3),
        'telefone': '(11) 92345-0003',
        'email': 'marcos.silva@email.com',
        'endereco': 'Rua Vergueiro, 300 - Vila Mariana, Sao Paulo/SP',
        'perfil': 'professor',
        'professor': {
            'formacao': 'Licenciatura em Historia - UNICAMP',
            'carga_horaria_max': 40,
        },
    },

    # ── Funcionarios (2) ───────────────────────────────────

    {
        'nome': 'Patricia Oliveira Nunes',
        'cpf': '678.901.234-69',
        'data_nascimento': date(1990, 4, 25),
        'telefone': '(11) 93456-0001',
        'email': 'patricia.nunes@email.com',
        'endereco': 'Rua Oscar Freire, 50 - Pinheiros, Sao Paulo/SP',
        'perfil': 'funcionario',
        'funcionario': {
            'cargo': 'Secretaria Escolar',
            'setor': 'Secretaria',
        },
    },
    {
        'nome': 'Jorge Luiz Batista',
        'cpf': '789.012.345-05',
        'data_nascimento': date(1988, 8, 12),
        'telefone': '(11) 93456-0002',
        'email': 'jorge.batista@email.com',
        'endereco': 'Rua Haddock Lobo, 80 - Cerqueira Cesar, Sao Paulo/SP',
        'perfil': 'funcionario',
        'funcionario': {
            'cargo': 'Coordenador Pedagogico',
            'setor': 'Coordenacao',
        },
    },

    # ── Pessoa sem perfil (1) ──────────────────────────────
    # Representa um cadastro generico (ex: responsavel de aluno,
    # contato externo). Nao possui vinculo com Aluno/Professor/Funcionario.

    {
        'nome': 'Claudia Regina Martins',
        'cpf': '890.123.456-42',
        'data_nascimento': date(1975, 6, 14),
        'telefone': '(11) 94567-0001',
        'email': 'claudia.martins@email.com',
        'endereco': 'Rua Bela Cintra, 150 - Jardins, Sao Paulo/SP',
        'perfil': None,
    },
]


class Command(BaseCommand):
    help = (
        'Popula o banco com dados iniciais da Etapa 1 '
        '(escola, pessoas, alunos, professores, funcionarios). '
        'Idempotente — pode rodar varias vezes sem duplicar dados.'
    )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Populando dados iniciais da Etapa 1...\n')

        self._criar_escola()
        self._criar_pessoas_e_perfis()
        self._imprimir_resumo()

    # ── Escola ──────────────────────────────────────────────

    def _criar_escola(self):
        self.stdout.write('--- Escola ---')
        escola, created = Escola.objects.get_or_create(
            cnpj=ESCOLA['cnpj'],
            defaults=ESCOLA,
        )
        status = self.style.SUCCESS('criada') if created else 'ja existia'
        self.stdout.write(f'  {escola.nome} — {status}')

    # ── Pessoas e perfis ────────────────────────────────────

    def _criar_pessoas_e_perfis(self):
        self.stdout.write('\n--- Pessoas ---')

        for item in PESSOAS:
            # Copia para nao alterar a lista original (idempotencia)
            data = dict(item)
            perfil = data.pop('perfil')
            aluno_data = data.pop('aluno', None)
            professor_data = data.pop('professor', None)
            funcionario_data = data.pop('funcionario', None)

            # Cria ou busca a Pessoa pelo CPF (campo unico)
            pessoa, created = Pessoa.objects.get_or_create(
                cpf=data['cpf'],
                defaults=data,
            )
            status = self.style.SUCCESS('criada') if created else 'ja existia'
            self.stdout.write(f'  {pessoa.nome} — {status}')

            # Cria o perfil vinculado, se aplicavel
            if perfil == 'aluno' and aluno_data:
                self._criar_aluno(pessoa, aluno_data)
            elif perfil == 'professor' and professor_data:
                self._criar_professor(pessoa, professor_data)
            elif perfil == 'funcionario' and funcionario_data:
                self._criar_funcionario(pessoa, funcionario_data)

    def _criar_aluno(self, pessoa, data):
        """Cria perfil de Aluno vinculado a uma Pessoa."""
        _, created = Aluno.objects.get_or_create(
            pessoa=pessoa,
            defaults=data,
        )
        if created:
            self.stdout.write(self.style.SUCCESS(
                f'    -> Aluno (matricula: {data["matricula"]})'
            ))

    def _criar_professor(self, pessoa, data):
        """Cria perfil de Professor vinculado a uma Pessoa."""
        _, created = Professor.objects.get_or_create(
            pessoa=pessoa,
            defaults=data,
        )
        if created:
            self.stdout.write(self.style.SUCCESS(
                f'    -> Professor ({data["formacao"]})'
            ))

    def _criar_funcionario(self, pessoa, data):
        """Cria perfil de Funcionario vinculado a uma Pessoa."""
        _, created = Funcionario.objects.get_or_create(
            pessoa=pessoa,
            defaults=data,
        )
        if created:
            self.stdout.write(self.style.SUCCESS(
                f'    -> Funcionario ({data["cargo"]})'
            ))

    # ── Resumo ──────────────────────────────────────────────

    def _imprimir_resumo(self):
        self.stdout.write('\n--- Resumo ---')
        self.stdout.write(f'  Escolas:       {Escola.objects.count()}')
        self.stdout.write(f'  Pessoas:       {Pessoa.objects.count()}')
        self.stdout.write(f'  Alunos:        {Aluno.objects.count()}')
        self.stdout.write(f'  Professores:   {Professor.objects.count()}')
        self.stdout.write(f'  Funcionarios:  {Funcionario.objects.count()}')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Seed concluido com sucesso.'))
