"""
Tests for the panel client views (ClientHomeView, ClientProcessDetailView,
ClientProfileView).

Client views resolve the Client by matching user.email (blank email matches
clients with blank default email). Tests that need a matching client create a
user with an explicit email AND a Client with that email.
"""

import pytest

from django.urls import reverse

from conftest import make_user, make_client, make_process_type, make_process


def _make_client_user(username, email):
    """Create a user with an explicit email + a Client with that email."""
    user = make_user(username, 'client')
    user.email = email
    user.save()
    client = make_client(
        email=email,
        first_name='Test',
        last_name='Client',
    )
    return user, client


@pytest.mark.django_db
class TestClientHomeView:
    """ClientHomeView resolves the client by user.email."""

    def test_matching_email_shows_client(self, client):
        user, client_obj = _make_client_user('cliente1', 'c1@example.com')
        client.force_login(user)
        response = client.get(reverse('panel:client_home'))
        assert response.status_code == 200
        assert response.context['client'] == client_obj

    def test_email_without_client_shows_none(self, client):
        """A user whose email matches no Client just gets client=None."""
        user = make_user('solo_user', 'client')
        user.email = 'nadie@example.com'
        user.save()
        client.force_login(user)
        response = client.get(reverse('panel:client_home'))
        assert response.status_code == 200
        assert response.context['client'] is None

    def test_duplicate_clients_same_blank_email_handled_gracefully(self, client, client_user):
        """Two Clients with the blank default email do NOT crash the view.

        Client.objects.get(email='') raises MultipleObjectsReturned when two
        Client rows share the blank '' email (the Client model default) and the
        logged in user also has email=''. MultipleObjectsReturned is NOT a
        subclass of DoesNotExist, so the view must catch it explicitly. The
        correct behavior is to degrade to client=None instead of a 500.
        """
        make_client()  # email defaults to ''
        make_client()  # second row with email=''
        client.force_login(client_user)
        response = client.get(reverse('panel:client_home'))
        assert response.status_code == 200
        assert response.context['client'] is None


@pytest.mark.django_db
class TestClientProcessDetailView:
    """Client can only view processes where process.client.email == user.email."""

    def test_process_of_this_client_200(self, client):
        user, client_obj = _make_client_user('cliente2', 'c2@example.com')
        ptype = make_process_type('Extranjería', 'extranjeria')
        process = make_process(client_obj, ptype)
        client.force_login(user)
        response = client.get(
            reverse('panel:client_process_detail', kwargs={'pk': process.pk})
        )
        assert response.status_code == 200

    def test_process_of_other_client_redirects_home(self, client):
        user, client_obj = _make_client_user('cliente3', 'c3@example.com')
        other_client = make_client(email='otro@example.com')
        ptype = make_process_type('Extranjería', 'extranjeria')
        process = make_process(other_client, ptype)
        client.force_login(user)
        response = client.get(
            reverse('panel:client_process_detail', kwargs={'pk': process.pk})
        )
        assert response.status_code == 302
        assert response.url == reverse('panel:client_home')


@pytest.mark.django_db
class TestClientProfileView:
    """ClientProfileView shows the client matching user.email."""

    def test_with_matching_email_shows_client(self, client):
        user, client_obj = _make_client_user('cliente4', 'c4@example.com')
        client.force_login(user)
        response = client.get(reverse('panel:client_profile'))
        assert response.status_code == 200
        assert response.context['client'] == client_obj

    def test_without_client_shows_none(self, client):
        user = make_user('cliente_sin', 'client')
        user.email = 'nadie2@example.com'
        user.save()
        client.force_login(user)
        response = client.get(reverse('panel:client_profile'))
        assert response.status_code == 200
        assert response.context['client'] is None
