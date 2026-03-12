from rest_framework import serializers

from courses.models import Course, Lesson, Subscription
from courses.validators import validate_youtube_url


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для подписки (используется внутри курса)
    """
    class Meta:
        model = Subscription
        fields = ['user', 'course', 'created_at']


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        # Добавляем валидатор для поля video_link
        extra_kwargs = {
            'video_link': {
                'validators': [validate_youtube_url]  # ← Подключаем валидатор
            }
        }


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'description',
            'preview',
            'created_at',
            'updated_at',
            'lessons_count',  # количество уроков
            'lessons',  # список уроков
            'is_subscribed',
        ]

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """
        Проверяет, подписан ли текущий пользователь на этот курс
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.subscriptions.filter(user=request.user).exists()
        return False

    def validate(self, attrs):
        """
        Проверка прав на создание/изменение
        """
        request = self.context.get('request')

        # Если это создание (POST)
        if request and request.method == 'POST':
            # Модераторы не могут создавать
            if request.user.groups.filter(name='Модераторы').exists():
                raise serializers.ValidationError(
                    "Модераторы не могут создавать новые курсы"
                )

        return attrs
