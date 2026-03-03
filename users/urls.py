# users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.apps import UsersConfig
from users.views import PaymentViewSet

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
]