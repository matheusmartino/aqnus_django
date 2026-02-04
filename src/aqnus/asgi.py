"""
ASGI config for aqnus project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os
import sys
from pathlib import Path

# Adiciona src/ ao Python path (necessario para entry points como uvicorn)
src_path = str(Path(__file__).resolve().parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aqnus.settings')

from django.core.asgi import get_asgi_application

application = get_asgi_application()
