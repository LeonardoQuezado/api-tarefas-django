API de Gerenciamento de Tarefas
API RESTful para gerenciamento de tarefas desenvolvida com Django REST Framework, autenticação JWT, cache Redis e containerização Docker.
🚀 Funcionalidades

Autenticação completa: Registro, login com JWT (access e refresh tokens)
CRUD de Tarefas: Criação, leitura, atualização e exclusão de tarefas
Sistema de Categorias: Organização de tarefas por categorias
Endpoint de Agenda: Listagem ordenada por data com filtros avançados
Cache Redis: Performance otimizada para consultas frequentes
Email de Boas-vindas: Notificação automática para novos usuários
Containerização: Deploy simplificado com Docker

🛠️ Tecnologias

Django 5.0+
Django REST Framework
JWT Authentication (djangorestframework-simplejwt)
PostgreSQL
Redis
Docker & Docker Compose
Celery (preparado para envio assíncrono de emails)

📋 Pré-requisitos

Docker e Docker Compose instalados
Git

🔧 Instalação e Execução
1. Clone o repositório
bashgit clone https://github.com/SEU-USUARIO/api-tarefas-django.git
cd api-tarefas-django
2. Execute com Docker
bashdocker-compose up --build
3. Acesse a aplicação

API: http://localhost:8000/api/
Admin: http://localhost:8000/admin/

4. Criar superusuário (opcional)
bashdocker-compose exec web python manage.py createsuperuser
📚 Documentação da API
Autenticação
Registro de Usuário
httpPOST /api/auth/register/
Content-Type: application/json

{
    "username": "usuario",
    "email": "usuario@email.com",
    "password": "senha123",
    "password_confirm": "senha123",
    "first_name": "Nome",
    "last_name": "Sobrenome"
}
Login
httpPOST /api/auth/login/
Content-Type: application/json

{
    "username": "usuario",
    "password": "senha123"
}
Refresh Token
httpPOST /api/auth/token/refresh/
Content-Type: application/json

{
    "refresh": "seu_refresh_token_aqui"
}
Tarefas
Listar Tarefas
httpGET /api/tasks/
Authorization: Bearer seu_access_token
Criar Tarefa
httpPOST /api/tasks/
Authorization: Bearer seu_access_token
Content-Type: application/json

{
    "title": "Título da tarefa",
    "description": "Descrição detalhada",
    "execution_date": "2025-07-25T10:00:00-03:00",
    "status": "pendente",
    "category_ids": [1, 2]
}
Agenda (com cache)
httpGET /api/tasks/agenda/
Authorization: Bearer seu_access_token

# Filtros opcionais:
GET /api/tasks/agenda/?execution_date=2025-07-25
GET /api/tasks/agenda/?status=pendente
GET /api/tasks/agenda/?categories=1
Categorias
Listar Categorias
httpGET /api/categories/
Authorization: Bearer seu_access_token
🔍 Status das Tarefas

pendente: Tarefa ainda não iniciada
em_andamento: Tarefa em execução
concluida: Tarefa finalizada

🏗️ Estrutura do Projeto
api-tarefas-django/
├── core/                   # Configurações do Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── tasks/                  # App principal
│   ├── models.py          # Modelos (Task, Category)
│   ├── serializers.py     # Serializers do DRF
│   ├── views.py           # Views e ViewSets
│   ├── urls.py            # URLs do app
│   └── admin.py           # Configuração do admin
├── requirements.txt       # Dependências Python
├── Dockerfile            # Configuração do container
├── docker-compose.yml    # Orquestração dos serviços
├── .env                  # Variáveis de ambiente
├── .gitignore           # Arquivos ignorados pelo Git
└── README.md            # Documentação
🔒 Segurança

Autenticação JWT obrigatória para todos os endpoints de tarefas
Usuários só podem ver/editar suas próprias tarefas
Validação de dados de entrada
Configuração de CORS para frontend