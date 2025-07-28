#  API de Gerenciamento de Tarefas

[![Tests](https://img.shields.io/badge/tests-12%2F12%20passing-brightgreen)](https://github.com/seu-usuario/api-tarefas-django)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/seu-usuario/api-tarefas-django)
[![Django](https://img.shields.io/badge/Django-5.2+-blue)](https://djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16+-blue)](https://www.django-rest-framework.org/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue)](https://docker.com/)

API RESTful completa para gerenciamento de tarefas desenvolvida com Django REST Framework, autenticação JWT, cache Redis e containerização Docker.

##  Índice

- [Funcionalidades](#-funcionalidades)
- [Tecnologias](#️-tecnologias)
- [Instalação e Execução](#-instalação-e-execução)
- [Documentação da API](#-documentação-da-api)
- [Estrutura do Projeto](#️-estrutura-do-projeto)
- [Variáveis de Ambiente](#-variáveis-de-ambiente)
- [Deploy](#-deploy)

##  Funcionalidades

### ✅ Autenticação Completa
-  Registro de usuários com validação
-  Login com JWT (access e refresh tokens)
-  Proteção de endpoints com autenticação obrigatória
-  Email de boas-vindas automático

### ✅ Gestão de Tarefas
-  CRUD completo (Create, Read, Update, Delete)
-  Sistema de categorias com relacionamento Many-to-Many
-  Isolamento por usuário (cada um vê apenas suas tarefas)
-  Ordenação por data de execução
-  Busca avançada por título, descrição, status e categorias

### ✅ Performance e Cache
-  Cache Redis no endpoint de agenda
-  Invalidação automática ao criar/editar/excluir tarefas
-  Paginação em todas as listagens

### ✅ Integração e Deploy
-  Containerização completa com Docker
-  Envio síncrono de emails com Celery
-  Suporte a PostgreSQL
-  Configuração via variáveis de ambiente

## 🛠️ Tecnologias

- **Backend:** Django 5.2.4, Django REST Framework 3.16
- **Autenticação:** JWT via djangorestframework-simplejwt
- **Banco de Dados:** PostgreSQL (Docker)
- **Cache:** Redis 7
- **Containerização:** Docker & Docker Compose
- **Email:** SMTP com Mailtrap (testado e funcionando)
- **Documentação:** Swagger/OpenAPI automática

## 🔧 Instalação e Execução

### 💼 Para Recrutadores (Setup Rápido)

Esta API está pronta para avaliação técnica:

- ✅ **Docker pronto:** `docker-compose up --build`
- ✅ **Configuração automática:** PostgreSQL + Redis + Django
- ✅ **Documentação interativa:** http://localhost:8000/api/docs/
- ✅ **Emails funcionando:** Configure .env para Mailtrap 
- ✅ **Dados de exemplo:** Categorias criadas automaticamente

### Pré-requisitos
- Docker e Docker Compose
- Git

### 🐳 Execução com Docker (Recomendado)

1. **Clone o repositório:**
```bash
git clone https://github.com/LeonardoQuezado/api-tarefas-django.git
cd api-tarefas-django
```

2. **Configure as variáveis de ambiente:**
```bash
touch .env
# Edite o arquivo .env com suas configurações
```

3. **Execute o projeto:**
```bash
docker-compose up --build
```

4. **Acesse a aplicação:**
- ** Documentação Swagger:** http://localhost:8000/api/docs/
- ** ReDoc:** http://localhost:8000/api/redoc/
- ** Admin Django:** http://localhost:8000/admin/
- ** API Base:** http://localhost:8000/api/

5. **Criar superusuário (opcional):**
```bash
docker-compose exec web python manage.py createsuperuser
```

### 💻 Execução Local (Desenvolvimento)

1. **Clone e configure o ambiente:**
```bash
git clone https://github.com/LeonardoQuezado/api-tarefas-django.git
cd api-tarefas-django
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Configure as variáveis de ambiente:**
```bash
touch .env
# Edite o arquivo .env com suas configurações
```

4. **Execute as migrações:**
```bash
python manage.py migrate
python manage.py createsuperuser
```

5. **Inicie o Redis (necessário para cache):**
```bash
docker run -d -p 6379:6379 redis:alpine
```

6. **Execute o servidor:**
```bash
python manage.py runserver
```

## 📚 Documentação da API

### 🎯 **Documentação Interativa (Swagger)**

- **📖 Swagger UI:** http://localhost:8000/api/docs/
- **📘 ReDoc:** http://localhost:8000/api/redoc/
- **📄 Schema OpenAPI:** http://localhost:8000/api/schema/

### 🔧 **Como testar a API:**

1. **Acesse a documentação Swagger** em http://localhost:8000/api/docs/
2. **Registre um usuário** usando o endpoint `POST /auth/register/`
3. **Faça login** em `POST /auth/login/` para obter o token JWT
4. **Clique em "Authorize"** no Swagger e cole o token: `Bearer {seu_token}`
5. **Teste todos os endpoints** diretamente na interface

### 🔐 Autenticação

#### Registro de Usuário
```http
POST /api/auth/register/
Content-Type: application/json

{
    "username": "usuario",
    "email": "usuario@email.com",
    "password": "senha123",
    "password_confirm": "senha123",
    "first_name": "Nome",
    "last_name": "Sobrenome"
}
```

**Resposta (201):**
```json
{
    "message": "Usuário criado com sucesso!",
    "user": {
        "id": 1,
        "username": "usuario",
        "email": "usuario@email.com",
        "first_name": "Nome",
        "last_name": "Sobrenome"
    },
    "tokens": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

#### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
    "username": "usuario",
    "password": "senha123"
}
```

#### Refresh Token
```http
POST /api/auth/token/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 📋 Tarefas

#### Listar Tarefas
```http
GET /api/tasks/
Authorization: Bearer {access_token}
```

**Parâmetros de consulta:**
- `search`: Busca por título ou descrição
- `status`: Filtrar por status (pendente, em_andamento, concluida)
- `categories`: Filtrar por categoria (ID)
- `ordering`: Ordenação (-created_at, execution_date, etc.)

#### Criar Tarefa
```http
POST /api/tasks/
Authorization: Bearer {access_token}
Content-Type: application/json

{
    "title": "Título da tarefa",
    "description": "Descrição detalhada",
    "execution_date": "2025-07-25T10:00:00-03:00",
    "status": "pendente",
    "category_ids": [1, 2]
}
```

#### Atualizar Tarefa
```http
PATCH /api/tasks/{id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
    "title": "Novo título",
    "status": "em_andamento"
}
```

#### Excluir Tarefa
```http
DELETE /api/tasks/{id}/
Authorization: Bearer {access_token}
```

#### Agenda (Endpoint Especial com Cache)
```http
GET /api/tasks/agenda/
Authorization: Bearer {access_token}
```

**Parâmetros de consulta:**
- `execution_date`: Filtrar por data (YYYY-MM-DD)
- `status`: Filtrar por status
- `categories`: Filtrar por categoria

**Resposta:**
```json
[
    {
        "id": 1,
        "title": "Minha tarefa",
        "execution_date": "2025-07-25T10:00:00-03:00",
        "status": "pendente",
        "categories": ["Trabalho", "Urgente"]
    }
]
```

### 🏷️ Categorias

#### Listar Categorias
```http
GET /api/categories/
Authorization: Bearer {access_token}
```

**Resposta:**
```json
{
    "count": 3,
    "results": [
        {
            "id": 1,
            "name": "Trabalho",
            "icon": "💼",
            "created_at": "2025-07-24T10:00:00-03:00"
        }
    ]
}
```

### 📊 Status das Tarefas

| Status | Descrição |
|--------|-----------|
| `pendente` | Tarefa ainda não iniciada |
| `em_andamento` | Tarefa em execução |
| `concluida` | Tarefa finalizada |

## 🧪 Exemplos de Uso

### Criar Tarefa Completa
```http
POST /api/tasks/
Authorization: Bearer {access_token}
Content-Type: application/json

{
    "title": "Reunião importante",
    "description": "Apresentação do projeto para cliente",
    "execution_date": "2025-07-27T14:00:00-03:00",
    "status": "pendente",
    "category_ids": [1, 3]
}
```

### Filtrar Agenda por Data
```http
GET /api/tasks/agenda/?execution_date=2025-07-26
Authorization: Bearer {access_token}
```
**Retorna apenas tarefas do dia 26/07/2025**

### Buscar Tarefas
```http
GET /api/tasks/?search=reunião&status=pendente
Authorization: Bearer {access_token}
```
**Busca "reunião" em tarefas pendentes**

### Agenda com Filtros Combinados
```http
GET /api/tasks/agenda/?execution_date=2025-07-26&status=pendente&categories=1
Authorization: Bearer {access_token}
```
**Tarefas de hoje, pendentes, da categoria 1**

## 🏗️ Estrutura do Projeto

```
api-tarefas-django/
├── 📁 core/                    # Configurações do Django
│   ├── settings.py            # Configurações principais
│   ├── urls.py               # URLs do projeto
│   ├── celery.py             # Configuração do Celery
│   └── wsgi.py               # WSGI para deploy
├── 📁 tasks/                   # App principal
│   ├── models.py             # Models (Task, Category)
│   ├── serializers.py        # Serializers do DRF
│   ├── views.py              # Views e ViewSets
│   ├── urls.py               # URLs do app
│   ├── admin.py              # Configuração do admin
│   └── tasks.py              # Tasks do Celery
├── 📁 tests/                   # Testes automatizados
│   ├── test_complete_api.py   # Testes funcionais
│   ├── test_email.py         # Testes de email
│   └── test_smtp.py          # Testes SMTP
├── 📄 requirements.txt        # Dependências Python
├── 📄 Dockerfile             # Container da aplicação
├── 📄 docker-compose.yml     # Orquestração dos serviços
├── 📄 .gitignore            # Arquivos ignorados
└── 📄 README.md             # Esta documentação
```

## 🔧 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Configurações do Django
DEBUG=True
SECRET_KEY=django-secret-key-for-development-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL no Docker)
DATABASE_URL=postgresql://user:password@postgres:5432/dbname

# Cache Redis (Redis no Docker)
REDIS_URL=redis://redis:6379/1

# Email Settings (Mailtrap - suas credenciais estão corretas)
EMAIL_HOST=sandbox.smtp.mailtrap.io
EMAIL_PORT=2525
EMAIL_HOST_USER=seu_usuario_mailtrap
EMAIL_HOST_PASSWORD=sua_senha_mailtrap
EMAIL_USE_TLS=True

# Configurações adicionais
DEFAULT_FROM_EMAIL=noreply@seudominio.com
```

### 📧 Configuração do Email (Mailtrap)

1. Acesse [Mailtrap.io](https://mailtrap.io)
2. Crie uma conta gratuita
3. Copie as credenciais SMTP do seu inbox
4. Cole no arquivo `.env`

## 🚀 Deploy

### Docker em Produção

1. **Configure as variáveis de produção:**
```env
DEBUG=False
SECRET_KEY=sua-chave-super-segura-para-producao
DATABASE_URL=postgresql://user:pass@seu-banco.com:5432/db
REDIS_URL=redis://seu-redis.com:6379/0
```

2. **Execute em produção:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Deploy Manual

1. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

2. **Configure o banco de dados:**
```bash
python manage.py migrate
python manage.py collectstatic
```

3. **Use um servidor WSGI como Gunicorn:**
```bash
gunicorn core.wsgi:application
```

## 🔒 Segurança

-  Autenticação JWT obrigatória para todos os endpoints de tarefas
-  Usuários só podem ver/editar suas próprias tarefas
-  Validação rigorosa de dados de entrada
-  Configuração de CORS para frontend
-  Senhas hasheadas com algoritmos seguros do Django
