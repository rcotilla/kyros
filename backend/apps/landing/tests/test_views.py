"""
Tests for the landing views (login, logout, contact) with django.test.Client.

Login behavior:
  - manager/admin     -> panel:home
  - operator          -> panel:operator_home
  - client            -> panel:client_home
  - user w/o profile  -> panel:home (fallback)

The conftest role users use password='pass1234'.
"""

import pytest

from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client

from apps.landing.models import ContactMessage

from conftest import make_user


def _login(client, username, password='pass1234'):
    return client.post(
        reverse('landing:login'),
        {'username': username, 'password': password},
    )


@pytest.mark.django_db
class TestLoginViewRoleRedirect:
    """Login redirects to the panel per the user's role."""

    def test_manager_redirects_to_panel_home(self, client, manager_user):
        response = _login(client, manager_user.username)
        assert response.status_code == 302
        assert response.url == reverse('panel:home')

    def test_operator_redirects_to_operator_home(self, client, operator_user):
        response = _login(client, operator_user.username)
        assert response.status_code == 302
        assert response.url == reverse('panel:operator_home')

    def test_client_redirects_to_client_home(self, client, client_user):
        response = _login(client, client_user.username)
        assert response.status_code == 302
        assert response.url == reverse('panel:client_home')


@pytest.mark.django_db
class TestLoginViewFailures:
    """Invalid/inactive/missing credentials all redirect to landing:home."""

    def test_invalid_credentials_redirect_home(self, client):
        response = _login(client, 'nadie', 'wrongpass')
        assert response.status_code == 302
        assert response.url == reverse('landing:home')

    def test_inactive_user_redirect_home(self, client):
        user = make_user('inactivo', 'manager')
        user.is_active = False
        user.save()
        response = _login(client, user.username)
        assert response.status_code == 302
        assert response.url == reverse('landing:home')

    def test_missing_fields_redirect_home(self, client):
        response = client.post(reverse('landing:login'), {})
        assert response.status_code == 302
        assert response.url == reverse('landing:home')


@pytest.mark.django_db
class TestLoginViewNoProfile:
    """A user without a UserProfile falls back to panel:home.

    LoginView checks hasattr(user, 'profile') and, when absent, redirects
    to panel:home. This is the current fallback behavior.
    """

    def test_user_without_profile_redirects_panel_home(self, client):
        plain = User.objects.create_user(username='plano', password='pass1234')
        response = _login(client, plain.username)
        assert response.status_code == 302
        assert response.url == reverse('panel:home')


@pytest.mark.django_db
class TestLogoutView:
    """GET /logout/ logs out and redirects to landing:home."""

    def test_logout_redirects_home(self, client, manager_user):
        client.force_login(manager_user)
        response = client.get(reverse('landing:logout'))
        assert response.status_code == 302
        assert response.url == reverse('landing:home')


@pytest.mark.django_db
class TestContactView:
    """Contact form POST creates a ContactMessage and redirects to #contacto."""

    def test_valid_post_creates_message_and_redirects(self, client):
        response = client.post(reverse('landing:contact'), {
            'nombre': 'Juan',
            'email': 'juan@example.com',
            'mensaje': 'Hola, quiero info.',
        })
        assert response.status_code == 302
        assert response.url == reverse('landing:home') + '#contacto'
        assert ContactMessage.objects.count() == 1
        msg = ContactMessage.objects.get()
        assert msg.name == 'Juan'
        assert msg.email == 'juan@example.com'

    def test_missing_field_does_not_create(self, client):
        response = client.post(reverse('landing:contact'), {
            'nombre': 'Juan',
            'email': 'juan@example.com',
            # mensaje missing
        })
        # It still redirects to #contacto but with the error message, and
        # does NOT persist a ContactMessage.
        assert response.status_code == 302
        assert response.url == reverse('landing:home') + '#contacto'
        assert ContactMessage.objects.count() == 0


@pytest.mark.django_db
class TestCSRFEnforcement:
    """POSTs to login are rejected with 403 when CSRF is enforced."""

    def test_login_without_csrf_token_403(self):
        csrf_client = Client(enforce_csrf_checks=True)
        response = csrf_client.post(
            reverse('landing:login'),
            {'username': 'x', 'password': 'y'},
        )
        assert response.status_code == 403
