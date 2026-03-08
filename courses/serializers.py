from rest_framework import serializers

from courses.models import Course, Lesson



class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

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
        ]

    def get_lessons_count(self, obj):
        return obj.lessons.count()

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
