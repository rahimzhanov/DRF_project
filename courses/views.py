from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course, Lesson, Subscription
from courses.paginators import CoursePaginator, LessonPaginator
from courses.permissions import IsModerator, IsOwner
from courses.serializers import CourseSerializer, LessonSerializer
from users.tasks import notify_course_subscribers
from django.utils import timezone


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    pagination_class = CoursePaginator

    def perform_create(self, serializer):
        """Автоматически привязываем курс к текущему пользователю"""
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        """
        После обновления курса отправляем уведомления подписчикам
        (не чаще раза в 4 часа)
        """
        course = self.get_object()

        # Сохраняем обновление
        updated_course = serializer.save()

        # Проверяем, нужно ли отправлять уведомление
        if updated_course.should_send_notification():
            # Обновляем время последнего уведомления
            updated_course.last_notification_sent = timezone.now()
            updated_course.save(update_fields=['last_notification_sent'])

            # Запускаем задачу
            notify_course_subscribers.delay(course.id)
            print(f'Уведомление отправлено подписчикам курса "{course.title}"')
        else:
            print(f'Уведомление не отправлено (последнее уведомление менее 4 часов назад)')

        return updated_course

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
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]

class LessonDestroyAPIView(generics.DestroyAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]  # Позже добавим владельцев


# courses/views.py - исправленный SubscriptionView
class SubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        user = request.user

        subscription = Subscription.objects.filter(
            user=user,
            course=course
        )

        if subscription.exists():
            subscription.delete()
            message = 'Подписка удалена'
            is_subscribed = False
            status_code = status.HTTP_200_OK
        else:
            Subscription.objects.create(
                user=user,
                course=course
            )
            message = 'Подписка добавлена'
            is_subscribed = True
            status_code = status.HTTP_201_CREATED

        return Response(
            {
                'message': message,
                'is_subscribed': is_subscribed,
                'course_id': course.id
            },
            status=status_code
        )