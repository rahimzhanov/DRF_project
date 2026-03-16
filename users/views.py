# users/views.py
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, generics, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from courses.models import Lesson, Course
from .models import Payment, User
from .serializers import PaymentCreateSerializer, PaymentSerializer, UserRegistrationSerializer
from courses.services import (
    create_stripe_product,
    create_stripe_price,
    create_stripe_checkout_session
)


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


class PaymentCreateView(APIView):
    """
    Создание платежа через Stripe
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user = request.user

        # Определяем, что оплачивается: курс или урок
        if data.get('course_id'):
            item = get_object_or_404(Course, id=data['course_id'])
            item_name = f"Курс: {item.title}"
            item_description = item.description
        else:
            item = get_object_or_404(Lesson, id=data['lesson_id'])
            item_name = f"Урок: {item.title}"
            item_description = item.description

        # Шаг 1: Создаем продукт в Stripe
        product = create_stripe_product(item_name, item_description)
        if not product:
            return Response(
                {'error': 'Ошибка создания продукта в Stripe'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Шаг 2: Создаем цену в Stripe (предположим, цена 1000 руб)
        # В реальном проекте цену нужно брать из модели
        amount = 1000.00
        price = create_stripe_price(amount, product.id)
        if not price:
            return Response(
                {'error': 'Ошибка создания цены в Stripe'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Шаг 3: Создаем сессию для оплаты
        session = create_stripe_checkout_session(
            price_id=price.id,
            success_url=data['success_url'],
            cancel_url=data['cancel_url']
        )
        if not session:
            return Response(
                {'error': 'Ошибка создания сессии оплаты'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Шаг 4: Сохраняем платеж в БД
        payment = Payment.objects.create(
            user=user,
            paid_course=item if data.get('course_id') else None,
            paid_lesson=item if data.get('lesson_id') else None,
            amount=amount,
            payment_method='transfer',
            stripe_product_id=product.id,
            stripe_price_id=price.id,
            stripe_session_id=session.id,
            stripe_payment_url=session.url,
            payment_status='pending'
        )

        # Шаг 5: Возвращаем ссылку на оплату
        return Response({
            'payment_id': payment.id,
            'payment_url': session.url,
            'message': 'Платеж создан, перейдите по ссылке для оплаты'
        }, status=status.HTTP_201_CREATED)


class PaymentStatusView(APIView):
    """
    Проверка статуса платежа
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)

        # Здесь можно получить статус из Stripe по payment.stripe_session_id
        # из courses.services import get_stripe_session_status

        return Response({
            'payment_id': payment.id,
            'status': payment.payment_status,
            'payment_url': payment.stripe_payment_url
        })