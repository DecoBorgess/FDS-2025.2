#!/bin/bash

# Caminho do seu projeto
PROJECT_DIR="/Users/bernardocavalcanticarneiroleao/Documents/fds/FDS-2025.2/cashpilot"

# Ativa o virtualenv
source "$PROJECT_DIR/../venv/bin/activate"

# Exporta a variável de settings do Django
export DJANGO_SETTINGS_MODULE=cashpilot.settings

# Sobe o Gunicorn
gunicorn --workers 3 --bind 0.0.0.0:8000 cashpilot.wsgi:application
