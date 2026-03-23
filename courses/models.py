from django.db import models
from django.utils import timezone
from datetime import timedelta


from config import settings


# Create your models here.
class Course(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название')
    preview = models.ImageField(upload_to='users/previews/', blank=True, null=True, verbose_name='Превью')
    description = models.TextField(verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(  # ← Добавить это поле
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses',
        null=True,  # Временно разрешаем null
        blank=True
    )
    last_notification_sent = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Последнее уведомление'
    )

    def should_send_notification(self):
        """
        Проверяет, нужно ли отправлять уведомление
        (не более одного уведомления за 4 часа)
        """
        if not self.last_notification_sent:
            return True

        four_hours_ago = timezone.now() - timedelta(hours=4)
        return self.last_notification_sent < four_hours_ago

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['-created_at']



class Lesson(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название')
    preview = models.ImageField(upload_to='users/previews/', blank=True, null=True, verbose_name='Превью')
    video_link =models.URLField(max_length=500, verbose_name='Ссылка на видео')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name='Курс')
    description = models.TextField(verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(  # ← Добавить это поле
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lessons',
        null=True,  # Временно разрешаем null
        blank=True
    )

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'


class Subscription(models.Model):
    """
    Модель подписки пользователя на курс
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользователь'
    )
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Курс'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата подписки'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        # Уникальность: один пользователь может подписаться на курс только один раз
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.email} подписан на {self.course.title}"
