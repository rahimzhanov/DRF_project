# users/serializers.py
from rest_framework import serializers
from .models import Payment, User


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Payment
    """
    # Добавляем дополнительные поля для удобства отображения
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'user',
            'user_email',
            'payment_date',
            'paid_course',
            'paid_lesson',
            'amount',
            'payment_method',
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, label='Подтверждение пароля')

    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'password2',
            'phone',
            'city',
            'avatar',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'phone': {'required': False},
            'city': {'required': False},
            'avatar': {'required': False},
        }

    def validate(self, attrs):
        """
        Проверка, что пароли совпадают
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        """
        Создание нового пользователя
        """
        # Удаляем password2 из данных (он не нужен в модели)
        validated_data.pop('password2')

        # Создаем пользователя
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data.get('phone', ''),
            city=validated_data.get('city', ''),
            avatar=validated_data.get('avatar', None)
        )
        return user

