from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser
from courses.models import Course, Lesson
# Create your models here.


class CustomUserManager(BaseUserManager):
    """
    Кастомный менеджер для модели User, который не требует username
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Создание обычного пользователя
        """
        if not email:
            raise ValueError('Email обязателен')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создание суперпользователя
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=35, verbose_name='Телефон', blank=True, null=True, help_text='Введите номер телефона')
    city = models.CharField(max_length=100, verbose_name='Город', blank=True, null=True, help_text='Введите город')
    avatar = models.ImageField(upload_to='users/avatars/', blank=True, null=True, verbose_name='Аватар')

    # Указываем, что для авторизации используется email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Не требуем дополнительных полей

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['email']
        default_related_name = 'custom_user'

    def __str__(self):
        return self.email


class Payment(models.Model):
    """
    Модель для хранения информации о платежах пользователей
    """
    # Способы оплаты (choices)
    CASH = 'cash'
    TRANSFER = 'transfer'
    PAYMENT_METHOD_CHOICES = [
        (CASH, 'Наличные'),
        (TRANSFER, 'Перевод на счет'),
    ]

    # Кто оплатил (связь с пользователем)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Пользователь'
    )

    # Дата и время оплаты
    payment_date = models.DateTimeField(
        auto_now_add=False,  # Не auto_now_add, чтобы можно было указать любую дату
        verbose_name='Дата оплаты',
        help_text='Укажите дату и время оплаты'
    )

    # Оплаченный курс (может быть пустым)
    paid_course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,  # Если курс удалят, в платеже останется NULL
        null=True,
        blank=True,
        related_name='payments',
        verbose_name='Оплаченный курс'
    )

    # Оплаченный урок (может быть пустым)
    paid_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,  # Если урок удалят, в платеже останется NULL
        null=True,
        blank=True,
        related_name='payments',
        verbose_name='Оплаченный урок'
    )

    # Сумма оплаты
    amount = models.DecimalField(
        max_digits=10,  # Максимальное количество цифр всего
        decimal_places=2,  # Количество знаков после запятой (копейки)
        verbose_name='Сумма оплаты',
        help_text='Укажите сумму в рублях'
    )

    # Способ оплаты
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
        default=TRANSFER,  # По умолчанию - перевод
        verbose_name='Способ оплаты'
    )

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']  # Сортировка по дате (сначала новые)

    def __str__(self):
        """
        Строковое представление платежа
        """
        if self.paid_course:
            item = f"курс '{self.paid_course.title}'"
        elif self.paid_lesson:
            item = f"урок '{self.paid_lesson.title}'"
        else:
            item = "неизвестно"

        return f"{self.user.email} - {item} - {self.amount} руб."

    def clean(self):
        """
        Валидация: должен быть оплачен либо курс, либо урок, но не оба
        """
        from django.core.exceptions import ValidationError

        if self.paid_course and self.paid_lesson:
            raise ValidationError('Нельзя оплатить одновременно курс и урок')

        if not self.paid_course and not self.paid_lesson:
            raise ValidationError('Должен быть указан оплаченный курс или урок')