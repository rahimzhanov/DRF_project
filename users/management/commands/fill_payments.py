# users/management/commands/fill_payments.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User, Payment
from courses.models import Course, Lesson


class Command(BaseCommand):
    help = 'Заполнение базы тестовыми платежами'

    def handle(self, *args, **options):
        # Проверяем, есть ли пользователи
        if User.objects.count() < 2:
            self.stdout.write(self.style.ERROR('Создайте хотя бы 2 пользователя'))
            return

        # Проверяем, есть ли курсы
        if Course.objects.count() == 0:
            self.stdout.write(self.style.ERROR('Создайте хотя бы 1 курс'))
            return

        # Получаем первого пользователя
        user1 = User.objects.first()
        user2 = User.objects.last()

        # Получаем первый курс и урок
        course = Course.objects.first()
        lesson = Lesson.objects.first() if Lesson.objects.exists() else None

        # Создаем платежи
        payments_data = [
            {
                'user': user1,
                'payment_date': timezone.now(),
                'paid_course': course,
                'paid_lesson': None,
                'amount': 15000.00,
                'payment_method': 'transfer'
            },
            {
                'user': user1,
                'payment_date': timezone.now(),
                'paid_course': None,
                'paid_lesson': lesson,
                'amount': 2500.00,
                'payment_method': 'cash'
            },
            {
                'user': user2,
                'payment_date': timezone.now(),
                'paid_course': course,
                'paid_lesson': None,
                'amount': 15000.00,
                'payment_method': 'transfer'
            },
        ]

        for payment_data in payments_data:
            Payment.objects.create(**payment_data)
            self.stdout.write(f'Создан платеж для {payment_data["user"].email}')

        self.stdout.write(self.style.SUCCESS('Все платежи успешно созданы!'))