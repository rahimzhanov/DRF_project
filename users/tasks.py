# users/tasks.py
from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from courses.models import Course

User = get_user_model()


@shared_task
def send_course_update_email(course_id, user_email, course_title):
    """
    Отправка email об обновлении курса
    """
    subject = f'Обновление курса: {course_title}'
    message = f"""
    Здравствуйте!

    Курс "{course_title}" был обновлен.

    Приятного обучения!

    ---
    С уважением, команда LMS
    """

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
def notify_course_subscribers(course_id):
    """
    Отправляет уведомления всем подписчикам курса
    """
    from courses.models import Course

    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return f'Курс {course_id} не найден'

    # Получаем всех подписчиков курса
    subscribers = course.subscriptions.select_related('user').all()

    if not subscribers:
        return f'Нет подписчиков у курса {course.title}'

    # Отправляем письмо каждому подписчику
    results = []
    for subscription in subscribers:
        result = send_course_update_email.delay(
            course_id=course.id,
            user_email=subscription.user.email,
            course_title=course.title
        )
        results.append(f'{subscription.user.email} - task_id: {result.id}')

    return {
        'course': course.title,
        'subscribers_count': subscribers.count(),
        'tasks': results
    }


@shared_task
def deactivate_inactive_users():
    """
    Блокировка пользователей, не заходивших более месяца
    """
    from django.utils import timezone
    from datetime import timedelta

    one_month_ago = timezone.now() - timedelta(days=30)
    inactive_users = User.objects.filter(
        last_login__lt=one_month_ago,
        is_active=True
    )

    count = inactive_users.update(is_active=False)
    return f'Заблокировано пользователей: {count}'