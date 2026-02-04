"""
Configurações do projeto AQNUS.

ERP Escolar - Gestão Educacional
Django 6.0 | Python 3.12
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # raiz do projeto
SRC_DIR = BASE_DIR / 'src'

SECRET_KEY = 'django-insecure-3hj6k_4b+sn6z_vyb05-krv33*=@6n^5oh($1xy+^le@6o(3yi'

DEBUG = True

ALLOWED_HOSTS = []


# ───────────────────────────────────────────────
# Apps
# ───────────────────────────────────────────────

INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps do projeto
    'core',
    'accounts',
    'people',
    'academic',
    'library',
    'web',
]


# ───────────────────────────────────────────────
# Middleware
# ───────────────────────────────────────────────

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ───────────────────────────────────────────────
# URLs e Templates
# ───────────────────────────────────────────────

ROOT_URLCONF = 'aqnus.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [SRC_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'aqnus.wsgi.application'


# ───────────────────────────────────────────────
# Banco de dados — PostgreSQL (padrão do projeto)
# ───────────────────────────────────────────────

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'aqnus',
        'USER': 'aqnus',
        'PASSWORD': 'aqnus',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Alternativa para testes locais rápidos (descomentar e comentar o bloco acima):
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# ───────────────────────────────────────────────
# Autenticação
# ───────────────────────────────────────────────

AUTH_USER_MODEL = 'accounts.Usuario'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ───────────────────────────────────────────────
# Internacionalização
# ───────────────────────────────────────────────

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# ───────────────────────────────────────────────
# Arquivos estáticos
# ───────────────────────────────────────────────

STATIC_URL = 'static/'

STATICFILES_DIRS = [SRC_DIR / 'static']

STATIC_ROOT = BASE_DIR / 'staticfiles'


# ───────────────────────────────────────────────
# Padrões
# ───────────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
