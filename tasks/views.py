from rest_framework import generics, viewsets, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import Task, Category
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer,
    TaskSerializer, 
    TaskListSerializer,
    CategorySerializer
)
from .tasks import send_welcome_email_task


@extend_schema_view(
    post=extend_schema(
        summary="Registrar novo usuário",
        description="Cria uma nova conta de usuário e envia email de boas-vindas automaticamente",
        tags=['auth'],
        examples=[
            OpenApiExample(
                'Exemplo de registro',
                value={
                    "username": "usuario_exemplo",
                    "email": "usuario@exemplo.com", 
                    "password": "senhaSegura123",
                    "password_confirm": "senhaSegura123",
                    "first_name": "João",
                    "last_name": "Silva"
                }
            )
        ]
    )
)
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Enviar email de boas-vindas
        self.send_welcome_email(user)
        
        # Gerar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Usuário criado com sucesso!',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    def send_welcome_email(self, user):
        """Enviar email de boas-vindas - FORÇANDO ENVIO SÍNCRONO para testes"""
        print(f"🔄 Enviando email de boas-vindas para: {user.email}")
        
        # FORÇAR envio síncrono para garantir que funcione
        try:
            send_mail(
                subject='Bem-vindo à API de Tarefas!',
                message=f'''
Olá {user.first_name or user.username}!

Bem-vindo à nossa API de gerenciamento de tarefas!

Sua conta foi criada com sucesso. Agora você pode:
- Criar e gerenciar suas tarefas
- Organizar por categorias
- Acompanhar seu progresso

Comece agora mesmo e organize sua produtividade!

Equipe API Tarefas
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            print(f"✅ Email enviado SÍNCRONAMENTE para: {user.email}")
            print(f"📧 Verifique no Mailtrap: https://mailtrap.io/inboxes")
            
        except Exception as e:
            print(f"❌ ERRO AO ENVIAR EMAIL: {e}")
            print(f"Verificar configurações SMTP no .env")


@extend_schema_view(
    post=extend_schema(
        summary="Fazer login",
        description="Autentica o usuário e retorna tokens JWT (access e refresh)",
        tags=['auth'],
        examples=[
            OpenApiExample(
                'Exemplo de login',
                value={
                    "username": "usuario_exemplo",
                    "password": "senhaSegura123"
                }
            )
        ]
    )
)
class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Login realizado com sucesso!',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


@extend_schema_view(
    list=extend_schema(
        summary="Listar tarefas do usuário",
        description="Retorna todas as tarefas do usuário autenticado com paginação",
        tags=['tasks']
    ),
    create=extend_schema(
        summary="Criar nova tarefa",
        description="Cria uma nova tarefa para o usuário autenticado",
        tags=['tasks']
    ),
    retrieve=extend_schema(
        summary="Obter tarefa específica",
        description="Retorna os detalhes de uma tarefa específica do usuário",
        tags=['tasks']
    ),
    update=extend_schema(
        summary="Atualizar tarefa",
        description="Atualiza uma tarefa existente (invalidação automática do cache)",
        tags=['tasks']
    ),
    partial_update=extend_schema(
        summary="Atualizar tarefa parcialmente", 
        description="Atualiza campos específicos de uma tarefa",
        tags=['tasks']
    ),
    destroy=extend_schema(
        summary="Excluir tarefa",
        description="Remove uma tarefa do usuário (invalidação automática do cache)",
        tags=['tasks']
    )
)
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'categories']
    search_fields = ['title', 'description']
    ordering_fields = ['execution_date', 'created_at']
    ordering = ['execution_date']

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).prefetch_related('categories')

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        # Invalidar cache do usuário
        cache_key = f"agenda_user_{self.request.user.id}"
        cache.delete(cache_key)

    def perform_update(self, serializer):
        serializer.save()
        # Invalidar cache do usuário
        cache_key = f"agenda_user_{self.request.user.id}"
        cache.delete(cache_key)

    def perform_destroy(self, instance):
        instance.delete()
        # Invalidar cache do usuário
        cache_key = f"agenda_user_{self.request.user.id}"
        cache.delete(cache_key)

    @extend_schema(
        summary="Agenda de tarefas (com cache)",
        description="""
        Endpoint especial que retorna as tarefas do usuário ordenadas por data de execução.
        
        **Funcionalidades:**
        - Cache Redis por usuário (15 minutos)
        - Invalidação automática ao criar/editar/excluir tarefas
        - Filtros avançados por data, status e categorias
        - Performance otimizada
        """,
        tags=['agenda'],
        parameters=[
            OpenApiParameter(
                'execution_date', 
                OpenApiTypes.DATE, 
                description='Filtrar por data específica (YYYY-MM-DD)'
            ),
            OpenApiParameter(
                'status', 
                OpenApiTypes.STR, 
                description='Filtrar por status',
                enum=['pendente', 'em_andamento', 'concluida']
            ),
            OpenApiParameter(
                'categories', 
                OpenApiTypes.INT, 
                description='Filtrar por categoria (ID)'
            ),
        ]
    )
    @action(detail=False, methods=['get'])
    def agenda(self, request):
        """Endpoint de agenda com cache"""
        # Criar cache key único por usuário e parâmetros de filtro
        query_params = request.query_params.dict()
        cache_key = f"agenda_user_{request.user.id}_{hash(str(sorted(query_params.items())))}"
        
        # Tentar obter do cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # Se não estiver no cache, buscar do banco
        queryset = self.get_queryset().order_by('execution_date')
        
        # Aplicar filtro de data (CORRIGIDO)
        execution_date = request.query_params.get('execution_date')
        if execution_date:
            try:
                # Converter string YYYY-MM-DD para objeto date
                date_obj = timezone.datetime.strptime(execution_date, '%Y-%m-%d').date()
                # Filtrar apenas pela DATA (ignorando hora)
                queryset = queryset.filter(execution_date__date=date_obj)
                print(f"🔍 Filtrando por data: {date_obj}")
                print(f"📊 Tarefas encontradas: {queryset.count()}")
            except ValueError:
                print(f"❌ Data inválida fornecida: {execution_date}")
                pass
        
        # Filtros adicionais
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            print(f"🔍 Filtrando por status: {status_filter}")
            
        category_filter = request.query_params.get('categories')
        if category_filter:
            try:
                category_id = int(category_filter)
                queryset = queryset.filter(categories__id=category_id)
                print(f"🔍 Filtrando por categoria ID: {category_id}")
            except ValueError:
                print(f"❌ Categoria inválida: {category_filter}")
        
        # Aplicar busca se fornecida
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
            print(f"🔍 Buscando por: {search}")
        
        serializer = TaskListSerializer(queryset, many=True)
        
        # Cachear por 15 minutos apenas se não houver filtros específicos
        if not any([execution_date, status_filter, category_filter, search]):
            cache.set(cache_key, serializer.data, 60 * 15)
        else:
            # Cache mais curto para filtros específicos
            cache.set(cache_key, serializer.data, 60 * 5)  # 5 minutos
        
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="Listar categorias",
        description="Retorna todas as categorias disponíveis para organizar tarefas",
        tags=['categories']
    ),
    retrieve=extend_schema(
        summary="Obter categoria específica",
        description="Retorna os detalhes de uma categoria específica",
        tags=['categories']  
    )
)
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]