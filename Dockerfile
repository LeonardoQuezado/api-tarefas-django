FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create directories
RUN mkdir -p /app/staticfiles /app/tasks/management/commands/

# Create the init_data command inline
RUN echo 'from django.core.management.base import BaseCommand\nfrom tasks.models import Category\n\nclass Command(BaseCommand):\n    help = "Initialize default data"\n    \n    def handle(self, *args, **options):\n        try:\n            if not Category.objects.exists():\n                Category.objects.create(name="Trabalho", icon="💼")\n                Category.objects.create(name="Pessoal", icon="👤")\n                Category.objects.create(name="Urgente", icon="🚨")\n                self.stdout.write("✅ Categorias criadas!")\n            else:\n                self.stdout.write("ℹ️ Categorias já existem")\n        except Exception as e:\n            self.stdout.write(f"❌ Erro: {e}")' > /app/tasks/management/commands/init_data.py

# Create __init__.py files if they don't exist
RUN touch /app/tasks/management/__init__.py /app/tasks/management/commands/__init__.py

EXPOSE 8000

# Default command (will be overridden by docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]