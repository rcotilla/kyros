"""
Tests for the core API auth/user endpoints (AuthStatusView, UserProfileViewSet).

Covers registration, auth status, password change, and profile update.
"""

import pytest

from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User

from apps.core.models import UserProfile

from conftest import make_user


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestRegister:
    """Public user registration via POST core:auth-register."""

    def test_register_creates_user_and_client_profile(self, api_client):
        payload = {
            'username': 'nuevo_usuario',
            'email': 'nuevo@example.com',
            'first_name': 'Ana',
            'last_name': 'Perez',
            'password': 'segura123',
            'password2': 'segura123',
        }
        response = api_client.post(reverse('core:auth-register'), payload, format='json')
        assert response.status_code == 201

        user = User.objects.get(username='nuevo_usuario')
        assert user.email == 'nuevo@example.com'
        profile = UserProfile.objects.get(user=user)
        # Registration only creates User + UserProfile (role client); it does
        # NOT create a Client row.
        assert profile.role.name == 'client'

    def test_register_mismatched_passwords_400(self, api_client):
        payload = {
            'username': 'otro',
            'email': 'otro@example.com',
            'first_name': 'A',
            'last_name': 'B',
            'password': 'segura123',
            'password2': 'distinta',
        }
        response = api_client.post(reverse('core:auth-register'), payload, format='json')
        assert response.status_code == 400
        assert not User.objects.filter(username='otro').exists()

    def test_register_missing_password2_400(self, api_client):
        payload = {
            'username': 'otro2',
            'email': 'otro2@example.com',
            'first_name': 'A',
            'last_name': 'B',
            'password': 'segura123',
        }
        response = api_client.post(reverse('core:auth-register'), payload, format='json')
        assert response.status_code == 400


@pytest.mark.django_db
class TestAuthStatus:
    """GET core:auth-status returns auth state and profile."""

    def test_status_with_profile(self, api_client, manager_user):
        api_client.force_authenticate(user=manager_user)
        response = api_client.get(reverse('core:auth-status'))
        assert response.status_code == 200
        assert response.data['authenticated'] is True
        assert response.data['profile'] is not None

    def test_status_without_profile_profile_is_none(self, api_client):
        """A user without a UserProfile gets status 200 with profile=None."""
        plain = User.objects.create_user(username='sin_perfil', password='x')
        api_client.force_authenticate(user=plain)
        response = api_client.get(reverse('core:auth-status'))
        assert response.status_code == 200
        assert response.data['authenticated'] is True
        assert response.data['profile'] is None


@pytest.mark.django_db
class TestChangePassword:
    """POST core:user-change-password changes the user's password."""

    def test_success_changes_password(self, api_client, manager_user):
        api_client.force_authenticate(user=manager_user)
        response = api_client.post(reverse('core:user-change-password'), {
            'old_password': 'pass1234',
            'new_password': 'nueva456',
            'new_password2': 'nueva456',
        }, format='json')
        assert response.status_code == 200
        manager_user.refresh_from_db()
        assert manager_user.check_password('nueva456') is True
        assert manager_user.check_password('pass1234') is False

    def test_old_password_invalid_400(self, api_client, manager_user):
        api_client.force_authenticate(user=manager_user)
        response = api_client.post(reverse('core:user-change-password'), {
            'old_password': 'incorrecta',
            'new_password': 'nueva456',
            'new_password2': 'nueva456',
        }, format='json')
        assert response.status_code == 400

    def test_new_passwords_mismatch_400(self, api_client, manager_user):
        api_client.force_authenticate(user=manager_user)
        response = api_client.post(reverse('core:user-change-password'), {
            'old_password': 'pass1234',
            'new_password': 'nueva456',
            'new_password2': 'distinta',
        }, format='json')
        assert response.status_code == 400


@pytest.mark.django_db
class TestUpdateProfile:
    """PUT core:user-update-profile updates only company/phone."""

    def test_updates_company_and_phone(self, api_client, manager_user):
        api_client.force_authenticate(user=manager_user)
        response = api_client.put(reverse('core:user-update-profile'), {
            'company': 'Estudio X',
            'phone': '+54 11 5555 5555',
        }, format='json')
        assert response.status_code == 200
        profile = UserProfile.objects.get(user=manager_user)
        assert profile.company == 'Estudio X'
        assert profile.phone == '+54 11 5555 5555'

    def test_foreign_field_username_is_ignored(self, api_client, manager_user):
        original_username = manager_user.username
        api_client.force_authenticate(user=manager_user)
        response = api_client.put(reverse('core:user-update-profile'), {
            'company': 'Estudio X',
            'username': 'hackeado',
        }, format='json')
        assert response.status_code == 200
        manager_user.refresh_from_db()
        assert manager_user.username == original_username
