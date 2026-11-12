"""
Tests for the clients DRF API (ClientViewSet).

Covers role-based visibility, CRUD operations, custom actions,
search, ordering, and authentication.
"""

import pytest

from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from apps.clients.models import Client
from apps.documents.models import Document
from apps.processes.models import Process

from conftest import (
    make_user, make_client, make_process_type, make_process,
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestClientViewSetScope:
    """Role-based scoping of the ClientViewSet list endpoint."""

    def test_admin_sees_all_clients(self, api_client, admin_user, manager_user):
        """Admin can list all clients."""
        make_client(manager=manager_user, first_name='Alpha', last_name='One')
        make_client(manager=manager_user, first_name='Beta', last_name='Two')
        api_client.force_authenticate(user=admin_user)

        response = api_client.get(reverse('clients:client-list'))
        assert response.status_code == 200
        assert len(response.data['results']) == 2

    def test_manager_sees_all_clients(self, api_client, manager_user, operator_user):
        """Manager can list all clients."""
        make_client(manager=manager_user, first_name='Gamma', last_name='Three')
        make_client(manager=operator_user, first_name='Delta', last_name='Four')
        api_client.force_authenticate(user=manager_user)

        response = api_client.get(reverse('clients:client-list'))
        assert response.status_code == 200
        assert len(response.data['results']) == 2

    def test_operator_sees_only_assigned(self, api_client, manager_user, operator_user):
        """Operator sees only clients assigned to them or created by them."""
        assigned = make_client(
            manager=operator_user, first_name='Assigned', last_name='Operator'
        )
        make_client(manager=manager_user, first_name='Other', last_name='Manager')
        api_client.force_authenticate(user=operator_user)

        response = api_client.get(reverse('clients:client-list'))
        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == assigned.pk


@pytest.mark.django_db
class TestClientViewSetCRUD:
    """Basic CRUD operations through the API."""

    def test_create_client(self, api_client, manager_user):
        """POST creates a client with created_by set."""
        api_client.force_authenticate(user=manager_user)
        payload = {
            'first_name': 'New',
            'last_name': 'Client',
            'document_type': 'dni',
            'document_number': '55555555',
            'email': 'new@example.com',
            'country': 'AR',
        }
        response = api_client.post(
            reverse('clients:client-list'), payload, format='json'
        )
        assert response.status_code == 201
        assert response.data['first_name'] == 'New'
        assert response.data['document_number'] == '55555555'

        created = Client.objects.get(document_number='55555555')
        assert created.created_by == manager_user

    def test_retrieve_client(self, api_client, manager_user, client):
        """GET detail returns the full client data."""
        api_client.force_authenticate(user=manager_user)
        response = api_client.get(
            reverse('clients:client-detail', kwargs={'pk': client.pk})
        )
        assert response.status_code == 200
        assert response.data['first_name'] == 'Juan'
        assert response.data['last_name'] == 'Perez'
        assert response.data['full_name'] == 'Juan Perez'

    def test_update_client(self, api_client, manager_user, client):
        """PATCH updates client fields."""
        api_client.force_authenticate(user=manager_user)
        response = api_client.patch(
            reverse('clients:client-detail', kwargs={'pk': client.pk}),
            {'first_name': 'Updated', 'email': 'updated@example.com'},
            format='json',
        )
        assert response.status_code == 200
        client.refresh_from_db()
        assert client.first_name == 'Updated'
        assert client.email == 'updated@example.com'

    def test_delete_client(self, api_client, manager_user, client):
        """DELETE removes the client."""
        api_client.force_authenticate(user=manager_user)
        response = api_client.delete(
            reverse('clients:client-detail', kwargs={'pk': client.pk})
        )
        assert response.status_code == 204
        assert not Client.objects.filter(pk=client.pk).exists()


@pytest.mark.django_db
class TestClientViewSetActions:
    """Custom actions: my_clients, processes, documents, pdf."""

    def test_my_clients_action(self, api_client, operator_user, assigned_client):
        """GET /my_clients/ returns only clients assigned to current user."""
        api_client.force_authenticate(user=operator_user)
        response = api_client.get(reverse('clients:client-my-clients'))
        assert response.status_code == 200
        assert isinstance(response.data, list)
        assert len(response.data) == 1
        assert response.data[0]['id'] == assigned_client.pk

    def test_processes_action(self, api_client, manager_user, client):
        """GET /{id}/processes/ returns processes for this client."""
        ptype = make_process_type('Extranjería', 'extranjeria')
        process = make_process(client, ptype)
        api_client.force_authenticate(user=manager_user)

        response = api_client.get(
            reverse('clients:client-processes', kwargs={'pk': client.pk})
        )
        assert response.status_code == 200
        assert isinstance(response.data, list)
        assert len(response.data) == 1
        assert response.data[0]['id'] == process.pk

    def test_documents_action(self, api_client, manager_user, client):
        """GET /{id}/documents/ returns documents for this client."""
        from django.core.files.uploadedfile import SimpleUploadedFile

        doc = Document.objects.create(
            owner=manager_user,
            title='Test Doc',
            client=client,
            file=SimpleUploadedFile('doc.pdf', b'%PDF', 'application/pdf'),
        )
        api_client.force_authenticate(user=manager_user)

        response = api_client.get(
            reverse('clients:client-documents', kwargs={'pk': client.pk})
        )
        assert response.status_code == 200
        assert isinstance(response.data, list)
        assert len(response.data) == 1
        assert response.data[0]['id'] == doc.pk

    def test_pdf_action(self, api_client, manager_user, client):
        """GET /{id}/pdf/ returns PDF or 503 if WeasyPrint unavailable."""
        api_client.force_authenticate(user=manager_user)
        response = api_client.get(
            reverse('clients:client-pdf', kwargs={'pk': client.pk})
        )
        # Either PDF generated (200) or WeasyPrint not installed (503)
        assert response.status_code in (200, 503)


@pytest.mark.django_db
class TestClientViewSetSearchAndOrdering:
    """Search and ordering parameters."""

    def test_search_clients(self, api_client, admin_user):
        """Search by name or document_number."""
        Client.objects.create(
            first_name='SearchName',
            last_name='Unique',
            document_type='dni',
            document_number='SEARCH01',
        )
        Client.objects.create(
            first_name='Other',
            last_name='Person',
            document_type='dni',
            document_number='OTHER001',
        )
        api_client.force_authenticate(user=admin_user)

        response = api_client.get(
            reverse('clients:client-list'), {'search': 'SearchName'}
        )
        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['full_name'] == 'SearchName Unique'

    def test_ordering_clients(self, api_client, admin_user):
        """Ordering by last_name."""
        Client.objects.create(
            first_name='Zeta',
            last_name='Anderson',
            document_type='dni',
            document_number='ORD00001',
        )
        Client.objects.create(
            first_name='Alpha',
            last_name='Zimmerman',
            document_type='dni',
            document_number='ORD00002',
        )
        api_client.force_authenticate(user=admin_user)

        response = api_client.get(
            reverse('clients:client-list'), {'ordering': 'last_name'}
        )
        assert response.status_code == 200
        results = response.data['results']
        assert 'Anderson' in results[0]['full_name']
        assert 'Zimmerman' in results[1]['full_name']


@pytest.mark.django_db
class TestClientViewSetAuthentication:
    """Authentication requirements."""

    def test_unauthenticated_401(self, api_client):
        """Unauthenticated requests return 401 or 403."""
        response = api_client.get(reverse('clients:client-list'))
        assert response.status_code in (401, 403)
