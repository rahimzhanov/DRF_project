# users/views.py
from rest_framework import viewsets, filters, generics, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Payment, User
from .serializers import PaymentSerializer, UserRegistrationSerializer


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


class UserRegistrationView(generics.CreateAPIView):
    """
    Представление для регистрации новых пользователей
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]  # Доступно всем (даже неавторизованным)

    def post(self, request, *args, **kwargs):
        """
        Обработка POST запроса на регистрацию
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Создаем токены для нового пользователя
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': {
                'id': user.id,
                'email': user.email,
                'phone': user.phone,
                'city': user.city,
            },
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Пользователь успешно зарегистрирован'
        }, status=status.HTTP_201_CREATED)