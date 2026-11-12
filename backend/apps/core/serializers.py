"""
Serializers for core app.

Converts Django models to/from JSON for REST API.
Used by Flet frontend for authentication and role management.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Role


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'name', 'description')
        read_only_fields = ('id',)


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'is_active', 'date_joined'
        )
        read_only_fields = ('id', 'date_joined')


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    role = RoleSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            'id', 'user', 'role', 'company', 'phone',
            'status', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users (registration).
    """
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    role_name = serializers.CharField(source='profile.role.name', read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'password', 'password2', 'role_name'
        )
        read_only_fields = ('id',)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password2')

        user = User.objects.create_user(
            **validated_data,
            password=password
        )
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError("Las nuevas contraseñas no coinciden.")
        return data
