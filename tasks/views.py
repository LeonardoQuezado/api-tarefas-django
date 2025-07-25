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

from .models import Task, Category
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer,
    TaskSerializer, 
    TaskListSerializer,
    CategorySerializer
)
from .tasks import send_welcome_email_task


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

    @action(detail=False, methods=['get'])
    def agenda(self, request):
        """Endpoint de agenda com cache"""
        cache_key = f"agenda_user_{request.user.id}"
        
        # Tentar obter do cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # Se não estiver no cache, buscar do banco
        queryset = self.get_queryset().order_by('execution_date')
        
        # Aplicar filtros se fornecidos
        execution_date = request.query_params.get('execution_date')
        if execution_date:
            try:
                date_obj = timezone.datetime.strptime(execution_date, '%Y-%m-%d').date()
                queryset = queryset.filter(execution_date__date=date_obj)
            except ValueError:
                pass
        
        # Filtros adicionais
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        category_filter = request.query_params.get('categories')
        if category_filter:
            queryset = queryset.filter(categories__id=category_filter)
        
        serializer = TaskListSerializer(queryset, many=True)
        
        # Cachear por 15 minutos
        cache.set(cache_key, serializer.data, 60 * 15)
        
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]