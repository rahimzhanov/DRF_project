from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):

    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=35, verbose_name='Телефон', blank=True, null=True, help_text='Введите номер телефона')
    city = models.CharField(max_length=100, verbose_name='Город', blank=True, null=True, help_text='Введите город')
    avatar = models.ImageField(upload_to='users/avatars/', blank=True, null=True, verbose_name='Аватар')

    # Указываем, что для авторизации используется email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # username все еще требуется для createsuperuser

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['email']
        default_related_name = 'custom_user'

    def __str__(self):
        return self.email