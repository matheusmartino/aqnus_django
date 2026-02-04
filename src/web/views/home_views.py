"""
web.views.home_views

Views da página inicial.
"""

from django.shortcuts import render


def home(request):
    return render(request, 'web/home.html')
