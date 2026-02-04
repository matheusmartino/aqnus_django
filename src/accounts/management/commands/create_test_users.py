"""
Management command para criar usuarios de teste da Etapa 1.

Uso:
    python manage.py create_test_users
"""

from django.core.management.base import BaseCommand

from accounts.models import Usuario
from people.models import Pessoa


USERS = [
    {
        'username': 'admin',
        'password': 'admin123',
        'first_name': 'Administrador',
        'last_name': 'AQNUS',
        'email': 'admin@aqnus.local',
        'papel': 'admin',
        'is_staff': True,
        'is_superuser': True,
        'pessoa_nome': 'Administrador Geral',
        'pessoa_cpf': '000.000.000-00',
    },
    {
        'username': 'secretaria',
        'password': 'secretaria123',
        'first_name': 'Maria',
        'last_name': 'da Silva',
        'email': 'secretaria@aqnus.local',
        'papel': 'secretaria',
        'is_staff': True,
        'is_superuser': False,
        'pessoa_nome': 'Maria da Silva',
        'pessoa_cpf': '111.111.111-11',
    },
    {
        'username': 'professor',
        'password': 'professor123',
        'first_name': 'Carlos',
        'last_name': 'Oliveira',
        'email': 'professor@aqnus.local',
        'papel': 'professor',
        'is_staff': True,
        'is_superuser': False,
        'pessoa_nome': 'Carlos Oliveira',
        'pessoa_cpf': '222.222.222-22',
    },
    {
        'username': 'biblioteca',
        'password': 'biblioteca123',
        'first_name': 'Ana',
        'last_name': 'Santos',
        'email': 'biblioteca@aqnus.local',
        'papel': 'biblioteca',
        'is_staff': True,
        'is_superuser': False,
        'pessoa_nome': 'Ana Santos',
        'pessoa_cpf': '333.333.333-33',
    },
]


class Command(BaseCommand):
    help = 'Cria usuarios de teste para a Etapa 1 (admin, secretaria, professor, biblioteca)'

    def handle(self, *args, **options):
        created_count = 0

        for data in USERS:
            username = data['username']

            if Usuario.objects.filter(username=username).exists():
                self.stdout.write(f'  Usuario "{username}" ja existe, pulando.')
                continue

            # Cria Pessoa vinculada
            pessoa, _ = Pessoa.objects.get_or_create(
                cpf=data['pessoa_cpf'],
                defaults={
                    'nome': data['pessoa_nome'],
                },
            )

            # Cria Usuario
            user = Usuario.objects.create_user(
                username=username,
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                papel=data['papel'],
                is_staff=data['is_staff'],
                is_superuser=data['is_superuser'],
                pessoa=pessoa,
            )

            tipo = 'superusuario' if user.is_superuser else user.papel
            self.stdout.write(self.style.SUCCESS(
                f'  Criado: {username} ({tipo}) — senha: {data["password"]}'
            ))
            created_count += 1

        self.stdout.write('')
        if created_count:
            self.stdout.write(self.style.SUCCESS(
                f'{created_count} usuario(s) criado(s) com sucesso.'
            ))
        else:
            self.stdout.write('Nenhum usuario novo criado (todos ja existiam).')
