# courses/paginators.py
from rest_framework.pagination import PageNumberPagination


class CoursePaginator(PageNumberPagination):
    """
    Пагинатор для списка курсов
    """
    page_size = 5  # Количество элементов на странице
    page_size_query_param = 'page_size'  # Клиент может менять размер страницы
    max_page_size = 50  # Максимальный размер страницы
    page_query_param = 'page'  # Название параметра для номера страницы


class LessonPaginator(PageNumberPagination):
    """
    Пагинатор для списка уроков
    """
    page_size = 10  # Для уроков можно больше
    page_size_query_param = 'page_size'
    max_page_size = 100