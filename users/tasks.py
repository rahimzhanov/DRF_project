# users/tasks.py
from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@shared_task
def send_course_update_email(user_email, course_title):
    """
    Отправка email об обновлении курса
    """
    from django.core.mail import send_mail
    from django.conf import settings

    subject = f'Обновление курса: {course_title}'
    message = f'Здравствуйте!\n\nКурс "{course_title}" был обновлен.\n\nПриятного обучения!'

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        return f'Email отправлен {user_email}'
    except Exception as e:
        return f'Ошибка отправки {user_email}: {e}'


@shared_task
def deactivate_inactive_users():
    """
    Блокировка пользователей, не заходивших более месяца
    """
    one_month_ago = timezone.now() - timedelta(days=30)
    inactive_users = User.objects.filter(
        last_login__lt=one_month_ago,
        is_active=True
    )

    count = inactive_users.update(is_active=False)
    return f'Заблокировано пользователей: {count}'