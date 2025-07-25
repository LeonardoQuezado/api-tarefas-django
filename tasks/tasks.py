from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_welcome_email_task(user_id, user_email, user_name):
    """Enviar email de boas-vindas de forma assíncrona"""
    try:
        send_mail(
            subject='Bem-vindo à API de Tarefas!',
            message=f'''
            Olá {user_name}!
            
            Bem-vindo à nossa API de gerenciamento de tarefas!
            
            Sua conta foi criada com sucesso. Agora você pode:
            - Criar e gerenciar suas tarefas
            - Organizar por categorias
            - Acompanhar seu progresso
            
            Comece agora mesmo e organize sua produtividade!
            
            Equipe API Tarefas
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        return f"Email enviado para {user_email}"
    except Exception as e:
        return f"Erro ao enviar email: {e}"