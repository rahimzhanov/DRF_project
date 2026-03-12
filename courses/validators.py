# courses/validators.py
from rest_framework.serializers import ValidationError


def validate_youtube_url(value):
    """
    Валидатор для проверки, что ссылка ведет на YouTube

    Аргументы:
        value - проверяемое значение (URL)

    Возвращает:
        value, если проверка пройдена

    Исключение:
        ValidationError, если ссылка не с youtube.com
    """
    # Проверяем, что ссылка содержит youtube.com
    if 'youtube.com' not in value and 'youtu.be' not in value:
        raise ValidationError(
            'Ссылка должна быть с YouTube (youtube.com или youtu.be)'
        )

    # Если все хорошо - возвращаем значение
    return value