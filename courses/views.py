from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course, Lesson, Subscription
from courses.paginators import CoursePaginator, LessonPaginator
from courses.permissions import IsModerator, IsOwner
from courses.serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    pagination_class = CoursePaginator

    def perform_create(self, serializer):
        """Автоматически привязываем курс к текущему пользователю"""
        serializer.save(owner=self.request.user)

    # Для разных действий - разные права
    def get_permissions(self):
        """
        Настройка прав в зависимости от действия
        """
        if self.action in ['list', 'retrieve']:
            # Просмотр списка и деталей - для модераторов и авторизованных
            permission_classes = [IsAuthenticated]
        elif self.action in ['create']:
            # Создание - только не для модераторов (потом добавим)
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update']:
            # Редактирование - для модераторов (потом добавим владельцев)
            permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action in ['destroy']:
            # Удаление - только для владельцев (позже)
            permission_classes = [IsAuthenticated, IsOwner]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModerator]
    def perform_create(self, serializer):
        """Автоматически привязываем урок к текущему пользователю"""
        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all().order_by('id')
    permission_classes = [IsAuthenticated]
    pagination_class = LessonPaginator


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated]


class LessonUpdateAPIView(generics.UpdateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()

    def get_permissions(self):
        """
        Редактирование доступно модераторам
        """
        return [IsAuthenticated(), IsModerator()]

class LessonDestroyAPIView(generics.DestroyAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]  # Позже добавим владельцев


class SubscriptionView(APIView):
    """
    APIView для управления подпиской на курс
    POST /api/courses/1/subscribe/ - подписаться/отписаться
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        """
        Обработка POST запроса:
        - Если подписка есть - удаляем
        - Если подписки нет - создаем
        """
        # Получаем курс или 404
        course = get_object_or_404(Course, id=course_id)
        user = request.user

        # Проверяем, есть ли уже подписка
        subscription = Subscription.objects.filter(
            user=user,
            course=course
        )

        if subscription.exists():
            # Если подписка есть - удаляем
            subscription.delete()
            message = 'Подписка удалена'
            status_code = status.HTTP_200_OK
        else:
            # Если подписки нет - создаем
            Subscription.objects.create(
                user=user,
                course=course
            )
            message = 'Подписка добавлена'
            status_code = status.HTTP_201_CREATED

        return Response(
            {'message': message, 'is_subscribed': not subscription.exists()},
            status=status_code
        )
