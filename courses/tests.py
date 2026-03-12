# courses/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from rest_framework import status
from .models import Course, Lesson, Subscription

User = get_user_model()


class LessonTestCase(TestCase):
    """
    Тесты для CRUD уроков и проверки прав доступа
    """

    def setUp(self):
        """
        Подготовка данных перед каждым тестом
        """
        # Создаем клиент для API-запросов
        self.client = APIClient()

        # Создаем группу модераторов
        self.moderator_group, _ = Group.objects.get_or_create(name='Модераторы')

        # Создаем обычного пользователя (владелец)
        self.owner_user = User.objects.create_user(
            email='owner@test.com',
            password='test123',
            phone='+123456789',
            city='Москва'
        )

        # Создаем второго обычного пользователя (не владелец)
        self.other_user = User.objects.create_user(
            email='other@test.com',
            password='test123',
            phone='+987654321',
            city='СПб'
        )

        # Создаем модератора
        self.moderator_user = User.objects.create_user(
            email='moder@test.com',
            password='test123',
            phone='+555555555',
            city='Казань'
        )
        self.moderator_user.groups.add(self.moderator_group)

        # Создаем курс
        self.course = Course.objects.create(
            title='Тестовый курс',
            description='Описание тестового курса',
            owner=self.owner_user
        )

        # Создаем урок (принадлежит owner_user)
        self.lesson = Lesson.objects.create(
            title='Тестовый урок',
            description='Описание тестового урока',
            video_link='https://youtube.com/watch?v=12345',
            course=self.course,
            owner=self.owner_user
        )

    def test_lesson_create_unauthorized(self):
        """
        Тест: Неавторизованный пользователь НЕ может создать урок
        """
        data = {
            'title': 'Новый урок',
            'description': 'Описание',
            'video_link': 'https://youtube.com/watch?v=67890',
            'course': self.course.id
        }

        response = self.client.post('/api/lessons/create/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lesson_create_authorized(self):
        """
        Тест: Авторизованный пользователь может создать урок
        """
        self.client.force_authenticate(user=self.owner_user)

        data = {
            'title': 'Новый урок',
            'description': 'Описание',
            'video_link': 'https://youtube.com/watch?v=67890',
            'course': self.course.id
        }

        response = self.client.post('/api/lessons/create/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)  # Был 1, стало 2
        self.assertEqual(Lesson.objects.last().owner, self.owner_user)

    def test_lesson_create_moderator_forbidden(self):
        """
        Тест: Модератор НЕ может создать урок
        """
        self.client.force_authenticate(user=self.moderator_user)

        data = {
            'title': 'Новый урок',
            'description': 'Описание',
            'video_link': 'https://youtube.com/watch?v=67890',
            'course': self.course.id
        }

        response = self.client.post('/api/lessons/create/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_update_owner(self):
        """
        Тест: Владелец может редактировать свой урок
        """
        self.client.force_authenticate(user=self.owner_user)

        data = {
            'title': 'Обновленный урок',
            'description': 'Новое описание',
            'video_link': 'https://youtube.com/watch?v=12345',
            'course': self.course.id
        }

        response = self.client.put(f'/api/lessons/{self.lesson.id}/update/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Обновленный урок')

    def test_lesson_update_moderator(self):
        """
        Тест: Модератор может редактировать чужой урок
        """
        self.client.force_authenticate(user=self.moderator_user)

        data = {
            'title': 'Изменено модератором',
            'description': 'Новое описание',
            'video_link': 'https://youtube.com/watch?v=12345',
            'course': self.course.id
        }

        response = self.client.put(f'/api/lessons/{self.lesson.id}/update/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Изменено модератором')

    def test_lesson_update_other_user_forbidden(self):
        """
        Тест: Чужой пользователь НЕ может редактировать урок
        """
        self.client.force_authenticate(user=self.other_user)

        data = {
            'title': 'Попытка взлома',
            'description': 'Чужое описание',
            'video_link': 'https://youtube.com/watch?v=12345'
        }

        response = self.client.put(f'/api/lessons/{self.lesson.id}/update/', data)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_lesson_delete_owner(self):
        """
        Тест: Владелец может удалить свой урок
        """
        self.client.force_authenticate(user=self.owner_user)

        response = self.client.delete(f'/api/lessons/{self.lesson.id}/delete/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_lesson_delete_moderator_forbidden(self):
        """
        Тест: Модератор НЕ может удалить чужой урок
        """
        self.client.force_authenticate(user=self.moderator_user)

        response = self.client.delete(f'/api/lessons/{self.lesson.id}/delete/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # или 404
        self.assertEqual(Lesson.objects.count(), 1)  # Урок должен остаться


class SubscriptionTestCase(TestCase):
    """
    Тесты для подписки на курсы
    """

    def setUp(self):
        """
        Подготовка данных перед каждым тестом
        """
        self.client = APIClient()

        # Создаем пользователя
        self.user = User.objects.create_user(
            email='user@test.com',
            password='test123'
        )

        # Создаем курс
        self.course = Course.objects.create(
            title='Тестовый курс',
            description='Описание',
            owner=self.user
        )

    def test_subscribe(self):
        """
        Тест: Пользователь может подписаться на курс
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.post(f'/api/courses/{self.course.id}/subscribe/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
        self.assertTrue(response.data['is_subscribed'])

        # Проверяем, что подписка создалась в БД
        self.assertTrue(Subscription.objects.filter(
            user=self.user,
            course=self.course
        ).exists())

    def test_unsubscribe(self):
        """
        Тест: Пользователь может отписаться от курса
        """
        # Сначала подписываемся
        Subscription.objects.create(
            user=self.user,
            course=self.course
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.post(f'/api/courses/{self.course.id}/subscribe/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')
        self.assertFalse(response.data['is_subscribed'])

        # Проверяем, что подписка удалилась
        self.assertFalse(Subscription.objects.filter(
            user=self.user,
            course=self.course
        ).exists())

    def test_subscribe_unauthorized(self):
        """
        Тест: Неавторизованный пользователь не может подписаться
        """
        response = self.client.post(f'/api/courses/{self.course.id}/subscribe/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_course_serializer_has_is_subscribed(self):
        """
        Тест: Сериализатор курса возвращает поле is_subscribed
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'/api/courses/{self.course.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_subscribed', response.data)
        self.assertFalse(response.data['is_subscribed'])  # Пока не подписан

        # Подписываемся
        Subscription.objects.create(
            user=self.user,
            course=self.course
        )

        # Проверяем снова
        response = self.client.get(f'/api/courses/{self.course.id}/')
        self.assertTrue(response.data['is_subscribed'])
