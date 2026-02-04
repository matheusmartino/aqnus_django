"""
Management command para popular o banco com dados da biblioteca (Etapa 4).

Uso:
    python manage.py seed_biblioteca

Pre-requisito:
    Os dados da Etapa 1 devem existir:
        python manage.py seed_data

Escopo (Etapa 4 — biblioteca escolar):
    - 5 Autores
    - 3 Editoras
    - 4 Assuntos
    - 6 Obras (com autores e editora vinculados)
    - 10 Exemplares (com codigos de patrimonio)
    - Emprestimos via BibliotecaService:
        - 1 emprestimo ativo (exemplar emprestado)
        - 1 emprestimo devolvido (exemplar disponivel)
        - 1 emprestimo atrasado (data prevista no passado)
        - 1 exemplar sem emprestimo (disponivel)

Caracteristicas:
    - Idempotente: verifica existencia antes de criar
    - Atomico: roda dentro de transaction.atomic
    - NAO altera dados das Etapas 1, 2 e 3
    - Usa BibliotecaService para garantir consistencia
"""

from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from people.models import Aluno
from library.models import Autor, Editora, Assunto, Obra, Exemplar, Emprestimo
from library.services import BibliotecaService


# ─────────────────────────────────────────────────────────────
# Dados ficticios — Autores
# ─────────────────────────────────────────────────────────────

AUTORES = [
    'Machado de Assis',
    'Monteiro Lobato',
    'Clarice Lispector',
    'Jorge Amado',
    'Cecilia Meireles',
]


# ─────────────────────────────────────────────────────────────
# Dados ficticios — Editoras
# ─────────────────────────────────────────────────────────────

EDITORAS = [
    'Companhia das Letras',
    'Editora Atica',
    'Editora Moderna',
]


# ─────────────────────────────────────────────────────────────
# Dados ficticios — Assuntos
# ─────────────────────────────────────────────────────────────

ASSUNTOS = [
    'Literatura Brasileira',
    'Ciencias',
    'Historia',
    'Infantojuvenil',
]


# ─────────────────────────────────────────────────────────────
# Dados ficticios — Obras
# ─────────────────────────────────────────────────────────────

OBRAS = [
    {
        'titulo': 'Dom Casmurro',
        'autores': ['Machado de Assis'],
        'editora': 'Companhia das Letras',
        'assunto': 'Literatura Brasileira',
        'isbn': '978-85-359-0277-9',
        'ano_publicacao': 1899,
    },
    {
        'titulo': 'O Sitio do Picapau Amarelo',
        'autores': ['Monteiro Lobato'],
        'editora': 'Editora Atica',
        'assunto': 'Infantojuvenil',
        'isbn': '978-85-08-12345-6',
        'ano_publicacao': 1920,
    },
    {
        'titulo': 'A Hora da Estrela',
        'autores': ['Clarice Lispector'],
        'editora': 'Companhia das Letras',
        'assunto': 'Literatura Brasileira',
        'isbn': '978-85-359-0456-8',
        'ano_publicacao': 1977,
    },
    {
        'titulo': 'Capitaes da Areia',
        'autores': ['Jorge Amado'],
        'editora': 'Companhia das Letras',
        'assunto': 'Literatura Brasileira',
        'isbn': '978-85-359-0789-7',
        'ano_publicacao': 1937,
    },
    {
        'titulo': 'Ou Isto ou Aquilo',
        'autores': ['Cecilia Meireles'],
        'editora': 'Editora Moderna',
        'assunto': 'Infantojuvenil',
        'isbn': '978-85-16-01234-5',
        'ano_publicacao': 1964,
    },
    {
        'titulo': 'Ciencias para Jovens Curiosos',
        'autores': [],
        'editora': 'Editora Moderna',
        'assunto': 'Ciencias',
        'isbn': '',
        'ano_publicacao': 2020,
    },
]


# ─────────────────────────────────────────────────────────────
# Dados ficticios — Exemplares
# ─────────────────────────────────────────────────────────────

EXEMPLARES = [
    {'obra_titulo': 'Dom Casmurro', 'codigo': 'BIB-0001', 'estado': 'bom'},
    {'obra_titulo': 'Dom Casmurro', 'codigo': 'BIB-0002', 'estado': 'regular'},
    {'obra_titulo': 'O Sitio do Picapau Amarelo', 'codigo': 'BIB-0003', 'estado': 'bom'},
    {'obra_titulo': 'O Sitio do Picapau Amarelo', 'codigo': 'BIB-0004', 'estado': 'bom'},
    {'obra_titulo': 'A Hora da Estrela', 'codigo': 'BIB-0005', 'estado': 'bom'},
    {'obra_titulo': 'Capitaes da Areia', 'codigo': 'BIB-0006', 'estado': 'ruim'},
    {'obra_titulo': 'Capitaes da Areia', 'codigo': 'BIB-0007', 'estado': 'bom'},
    {'obra_titulo': 'Ou Isto ou Aquilo', 'codigo': 'BIB-0008', 'estado': 'bom'},
    {'obra_titulo': 'Ciencias para Jovens Curiosos', 'codigo': 'BIB-0009', 'estado': 'bom'},
    {'obra_titulo': 'Ciencias para Jovens Curiosos', 'codigo': 'BIB-0010', 'estado': 'regular'},
]


class Command(BaseCommand):
    help = (
        'Popula o banco com dados da biblioteca (Etapa 4). '
        'Idempotente — pode rodar varias vezes sem duplicar dados. '
        'Requer: seed_data (Etapa 1).'
    )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Populando dados da biblioteca (Etapa 4)...\n')

        if not self._validar_prerequisitos():
            return

        self._criar_autores()
        self._criar_editoras()
        self._criar_assuntos()
        self._criar_obras()
        self._criar_exemplares()
        self._criar_emprestimos()
        self._imprimir_resumo()

    # ── Validacao ──────────────────────────────────────────

    def _validar_prerequisitos(self):
        """Verifica se os dados da Etapa 1 existem."""
        if Aluno.objects.count() == 0:
            self.stderr.write(self.style.ERROR(
                'Nenhum aluno encontrado. Execute primeiro:\n'
                '  python manage.py seed_data'
            ))
            return False
        return True

    # ── Autores ───────────────────────────────────────────

    def _criar_autores(self):
        self.stdout.write('--- Autores ---')
        for nome in AUTORES:
            _, created = Autor.objects.get_or_create(nome=nome)
            status = self.style.SUCCESS('criado') if created else 'ja existia'
            self.stdout.write(f'  {nome} — {status}')

    # ── Editoras ──────────────────────────────────────────

    def _criar_editoras(self):
        self.stdout.write('\n--- Editoras ---')
        for nome in EDITORAS:
            _, created = Editora.objects.get_or_create(nome=nome)
            status = self.style.SUCCESS('criada') if created else 'ja existia'
            self.stdout.write(f'  {nome} — {status}')

    # ── Assuntos ──────────────────────────────────────────

    def _criar_assuntos(self):
        self.stdout.write('\n--- Assuntos ---')
        for nome in ASSUNTOS:
            _, created = Assunto.objects.get_or_create(nome=nome)
            status = self.style.SUCCESS('criado') if created else 'ja existia'
            self.stdout.write(f'  {nome} — {status}')

    # ── Obras ─────────────────────────────────────────────

    def _criar_obras(self):
        self.stdout.write('\n--- Obras ---')
        for item in OBRAS:
            editora = Editora.objects.filter(nome=item['editora']).first()
            assunto = Assunto.objects.filter(nome=item['assunto']).first()

            defaults = {
                'editora': editora,
                'assunto': assunto,
                'ano_publicacao': item['ano_publicacao'],
            }

            if item['isbn']:
                obra, created = Obra.objects.get_or_create(
                    isbn=item['isbn'],
                    defaults={**defaults, 'titulo': item['titulo']},
                )
            else:
                obra, created = Obra.objects.get_or_create(
                    titulo=item['titulo'],
                    defaults=defaults,
                )

            if created and item['autores']:
                autores = Autor.objects.filter(nome__in=item['autores'])
                obra.autores.set(autores)

            status = self.style.SUCCESS('criada') if created else 'ja existia'
            self.stdout.write(f'  {obra.titulo} — {status}')

    # ── Exemplares ────────────────────────────────────────

    def _criar_exemplares(self):
        self.stdout.write('\n--- Exemplares ---')
        for item in EXEMPLARES:
            obra = Obra.objects.filter(titulo=item['obra_titulo']).first()
            if not obra:
                self.stdout.write(self.style.WARNING(
                    f'  Obra "{item["obra_titulo"]}" nao encontrada, pulando.'
                ))
                continue

            _, created = Exemplar.objects.get_or_create(
                codigo_patrimonio=item['codigo'],
                defaults={
                    'obra': obra,
                    'estado_fisico': item['estado'],
                },
            )
            status = self.style.SUCCESS('criado') if created else 'ja existia'
            self.stdout.write(f'  {item["codigo"]} ({obra.titulo}) — {status}')

    # ── Emprestimos ───────────────────────────────────────

    def _criar_emprestimos(self):
        self.stdout.write('\n--- Emprestimos ---')

        alunos = list(Aluno.objects.all()[:3])
        if len(alunos) < 3:
            self.stdout.write(self.style.WARNING(
                '  Menos de 3 alunos encontrados, pulando emprestimos.'
            ))
            return

        hoje = date.today()

        # 1. Emprestimo ativo (BIB-0001 emprestado ao aluno 1)
        self._criar_emprestimo(
            codigo='BIB-0001',
            aluno=alunos[0],
            data_emprestimo=hoje - timedelta(days=3),
            data_prevista=hoje + timedelta(days=11),
            descricao='emprestimo ativo',
        )

        # 2. Emprestimo devolvido (BIB-0003 devolvido pelo aluno 2)
        self._criar_emprestimo_devolvido(
            codigo='BIB-0003',
            aluno=alunos[1],
            data_emprestimo=hoje - timedelta(days=20),
            data_prevista=hoje - timedelta(days=6),
            data_devolucao=hoje - timedelta(days=7),
            descricao='emprestimo devolvido',
        )

        # 3. Emprestimo atrasado (BIB-0005 atrasado pelo aluno 3)
        self._criar_emprestimo(
            codigo='BIB-0005',
            aluno=alunos[2],
            data_emprestimo=hoje - timedelta(days=30),
            data_prevista=hoje - timedelta(days=16),
            descricao='emprestimo atrasado',
        )

        # Atualiza emprestimos atrasados
        atrasados = BibliotecaService.atualizar_emprestimos_atrasados()
        if atrasados:
            self.stdout.write(self.style.SUCCESS(
                f'  {atrasados} emprestimo(s) marcado(s) como atrasado(s)'
            ))

    def _criar_emprestimo(self, codigo, aluno, data_emprestimo,
                          data_prevista, descricao):
        """Cria um emprestimo via service (idempotente)."""
        exemplar = Exemplar.objects.filter(
            codigo_patrimonio=codigo,
        ).first()
        if not exemplar:
            self.stdout.write(self.style.WARNING(
                f'  Exemplar {codigo} nao encontrado, pulando.'
            ))
            return

        # Verifica se ja existe emprestimo para este exemplar
        if Emprestimo.objects.filter(
            exemplar=exemplar,
            aluno=aluno,
        ).exists():
            self.stdout.write(f'  {descricao} ({codigo}) — ja existia')
            return

        try:
            BibliotecaService.emprestar_exemplar(
                exemplar=exemplar,
                aluno=aluno,
                data_emprestimo=data_emprestimo,
                data_prevista_devolucao=data_prevista,
            )
            self.stdout.write(self.style.SUCCESS(
                f'  {descricao} ({codigo} -> {aluno}) — criado'
            ))
        except Exception as e:
            self.stdout.write(self.style.WARNING(
                f'  {descricao} ({codigo}): {e}'
            ))

    def _criar_emprestimo_devolvido(self, codigo, aluno, data_emprestimo,
                                     data_prevista, data_devolucao, descricao):
        """Cria um emprestimo ja devolvido (idempotente)."""
        exemplar = Exemplar.objects.filter(
            codigo_patrimonio=codigo,
        ).first()
        if not exemplar:
            self.stdout.write(self.style.WARNING(
                f'  Exemplar {codigo} nao encontrado, pulando.'
            ))
            return

        # Verifica se ja existe emprestimo para este exemplar/aluno
        if Emprestimo.objects.filter(
            exemplar=exemplar,
            aluno=aluno,
        ).exists():
            self.stdout.write(f'  {descricao} ({codigo}) — ja existia')
            return

        try:
            emprestimo = BibliotecaService.emprestar_exemplar(
                exemplar=exemplar,
                aluno=aluno,
                data_emprestimo=data_emprestimo,
                data_prevista_devolucao=data_prevista,
            )
            BibliotecaService.devolver_exemplar(
                emprestimo=emprestimo,
                data_devolucao=data_devolucao,
            )
            self.stdout.write(self.style.SUCCESS(
                f'  {descricao} ({codigo} -> {aluno}) — criado e devolvido'
            ))
        except Exception as e:
            self.stdout.write(self.style.WARNING(
                f'  {descricao} ({codigo}): {e}'
            ))

    # ── Resumo ────────────────────────────────────────────

    def _imprimir_resumo(self):
        self.stdout.write('\n--- Resumo Etapa 4 ---')
        self.stdout.write(f'  Autores:      {Autor.objects.count()}')
        self.stdout.write(f'  Editoras:     {Editora.objects.count()}')
        self.stdout.write(f'  Assuntos:     {Assunto.objects.count()}')
        self.stdout.write(f'  Obras:        {Obra.objects.count()}')
        self.stdout.write(f'  Exemplares:   {Exemplar.objects.count()}')
        self.stdout.write(f'  Emprestimos:  {Emprestimo.objects.count()}')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            'Seed da biblioteca concluido com sucesso.'
        ))
