from __future__ import annotations

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from apps.core.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя"""
    password = serializers.CharField(validators=[validate_password],
                                     write_only=True, style={'input_type': 'password'})
    password_repeat = serializers.CharField(write_only=True,
                                            style={'input_type': 'password'}, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'password_repeat')

    def validate(self, attrs):
        """Проверка введенного повторно пароля на валидность"""
        if not attrs.get('password_repeat', None):
            raise ValidationError('Required field')
        if attrs['password'] != attrs['password_repeat']:
            raise ValidationError('Password does not match')
        return attrs

    def create(self, validated_data: dict):
        """Создание нового пользователя и сохранение его в БД с захэшированным паролем"""
        del validated_data['password_repeat']
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        return user


class LoginSerializer(serializers.ModelSerializer):
    """Сериализатор для входа по username и password"""
    password = serializers.CharField(validators=[validate_password],
                                     write_only=True, style={'input_type': 'password'})
    username = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password')
        read_only_fields = ('id', 'first_name', 'last_name', 'email')

    def create(self, validated_data: dict) -> User:
        """Аутентификация пользователя"""
        if not (user := authenticate(
                username=validated_data.get('username', None),
                password=validated_data.get('password', None)
        )):
            raise AuthenticationFailed
        return user


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для редактирования данных пользователя"""
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')
        read_only_fields = ('id',)


class UpdatePasswordSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления пароля"""
    old_password = serializers.CharField(validators=[validate_password], required=True,
                                         write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(validators=[validate_password], required=True,
                                         write_only=True, style={'input_type': 'password'})

    def validate_old_password(self, old_password: str):
        """Проверка на валидность введенного старого пароля"""
        if not self.instance.check_password(old_password):
            raise ValidationError('Incorrect password')
        return old_password

    def update(self, instance, validated_data: dict):
        """Обновление пароля"""
        instance.set_password(validated_data['new_password'])
        instance.save(update_fields=('password',))
        return instance

    class Meta:
        model = User
        fields = ('old_password', 'new_password')
