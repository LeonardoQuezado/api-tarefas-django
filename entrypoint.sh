#!/bin/bash

# Script de entrada para aguardar o PostgreSQL e executar migrações

set -e

# Função para aguardar o PostgreSQL ficar pronto
wait_for_postgres() {
    echo "🔄 Aguardando PostgreSQL ficar disponível..."
    
    while ! python -c "
import psycopg2
import os
import sys
try:
    conn = psycopg2.connect(
        host='db',
        database='tasks_db', 
        user='tasks_user',
        password='tasks_password'
    )
    conn.close()
    print('✅ PostgreSQL está pronto!')
    sys.exit(0)
except psycopg2.OperationalError:
    sys.exit(1)
"; do
        echo "⏳ PostgreSQL ainda não está pronto, aguardando..."
        sleep 2
    done
}

# Aguardar PostgreSQL
wait_for_postgres

echo "📋 Executando migrações..."
python manage.py migrate

echo "🏗️ Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "👤 Criando categorias padrão se não existirem..."
python manage.py shell -c "
from tasks.models import Category
if not Category.objects.exists():
    Category.objects.create(name='Trabalho', icon='💼')
    Category.objects.create(name='Pessoal', icon='👤') 
    Category.objects.create(name='Urgente', icon='🚨')
    print('✅ Categorias padrão criadas!')
else:
    print('ℹ️ Categorias já existem')
"

echo "🚀 Iniciando servidor Django..."
exec "$@"