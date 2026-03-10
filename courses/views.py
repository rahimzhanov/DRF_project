from rest_framework import  viewsets, generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from courses.models import Course, Lesson
from courses.permissions import IsModerator, IsOwner
from courses.serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()

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
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated]

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