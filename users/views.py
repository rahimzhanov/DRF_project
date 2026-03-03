# users/views.py
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с платежами
    Поддерживает:
    - Сортировку по дате
    - Фильтрацию по курсу, уроку и способу оплаты
    """
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all().order_by('-payment_date')  # По умолчанию сортировка

    # Подключаем бэкенды для фильтрации и сортировки
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    # Поля, по которым можно фильтровать
    filterset_fields = {
        'paid_course': ['exact', 'isnull'],  # фильтр по курсу (равно или null)
        'paid_lesson': ['exact', 'isnull'],  # фильтр по уроку
        'payment_method': ['exact'],  # фильтр по способу оплаты
        'user': ['exact'],  # фильтр по пользователю
    }

    # Поля, по которым можно сортировать
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']  # сортировка по умолчанию