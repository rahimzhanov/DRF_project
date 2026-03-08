# courses/permissions.py
from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """
    Разрешение для модераторов:
    - Могут просматривать и редактировать любые курсы/уроки
    - Не могут создавать и удалять
    """

    def has_permission(self, request, view):
        """
        Проверка прав на уровне всего запроса
        """
        # Только для авторизованных пользователей
        if not request.user or not request.user.is_authenticated:
            return False

        # Проверяем, состоит ли пользователь в группе "Модераторы"
        return request.user.groups.filter(name='Модераторы').exists()

    def has_object_permission(self, request, view, obj):
        """
        Проверка прав на уровне конкретного объекта
        Для модераторов разрешаем просмотр и редактирование любых объектов
        """
        # Для безопасных методов (GET, HEAD, OPTIONS) - разрешаем
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для изменения (PUT, PATCH) - разрешаем модераторам
        if request.method in ['PUT', 'PATCH']:
            return request.user.groups.filter(name='Модераторы').exists()

        # Для создания (POST) и удаления (DELETE) - запрещаем
        return False


class IsOwner(permissions.BasePermission):
    """
    Разрешение для владельца объекта
    """

    def has_object_permission(self, request, view, obj):
        # Проверяем, что у объекта есть поле owner и оно равно текущему пользователю
        return  hasattr(obj, 'owner') and obj.owner == request.user