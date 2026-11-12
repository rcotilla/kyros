"""
Tests for the processes DRF API (ProcessViewSet, ProcessTypeViewSet).
"""

import pytest

from rest_framework.test import APIClient
from django.urls import reverse

from apps.processes.models import ProcessStep

from conftest import (
    make_user, make_process_type, make_client, make_process,
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestProcessViewSetScope:
    """Role-based scoping of the ProcessViewSet list endpoint.

    NOTE: The viewset's get_queryset gives 'admin' AND 'manager' access to
    every process. Only other roles (operator/client) are filtered by their
    involvement. These tests assert that ACTUAL behavior.
    """

    def _setup(self, manager, other_manager, operator):
        ptype = make_process_type('Extranjería', 'extranjeria')
        client1 = make_client(manager=manager)
        client2 = make_client(manager=other_manager)
        p1 = make_process(client1, ptype, gestor=manager)
        p2 = make_process(client2, ptype, gestor=other_manager)
        p2.operator = operator
        p2.save()
        return p1, p2

    def test_admin_sees_all_processes(self, api_client, admin_user, manager_user, other_manager, operator_user):
        self._setup(manager_user, other_manager, operator_user)
        api_client.force_authenticate(user=admin_user)

        response = api_client.get(reverse('processes:process-list'))
        assert response.status_code == 200
        assert len(response.data['results']) == 2

    def test_manager_sees_all_processes(self, api_client, manager_user, other_manager, operator_user):
        """Managers (and admins) are granted full visibility by the viewset."""
        self._setup(manager_user, other_manager, operator_user)
        api_client.force_authenticate(user=manager_user)

        response = api_client.get(reverse('processes:process-list'))
        assert response.status_code == 200
        assert len(response.data['results']) == 2

    def test_operator_sees_only_involved_processes(self, api_client, manager_user, other_manager, operator_user):
        """Non-manager roles are filtered to processes they are involved in."""
        p1, p2 = self._setup(manager_user, other_manager, operator_user)
        api_client.force_authenticate(user=operator_user)

        response = api_client.get(reverse('processes:process-list'))
        assert response.status_code == 200
        # Only p2 (which has this operator assigned) is visible to the operator.
        # The list serializer exposes `id`/`file_number`, not `operator`.
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == p2.pk


@pytest.mark.django_db
class TestProcessViewSetByStatus:
    def test_by_status_returns_counts_dict(self, api_client, admin_user, manager_user):
        ptype = make_process_type('Extranjería', 'extranjeria')
        client = make_client(manager=manager_user)
        make_process(client, ptype, status='pending')
        make_process(client, ptype, status='pending')
        make_process(client, ptype, status='completed')
        api_client.force_authenticate(user=admin_user)

        response = api_client.get(reverse('processes:process-by-status'))
        assert response.status_code == 200
        data = response.data
        assert data['pending'] == 2
        assert data['completed'] == 1
        assert data['approved'] == 0


@pytest.mark.django_db
class TestProcessViewSetAddStep:
    def test_add_step_creates_process_step(self, api_client, admin_user, manager_user):
        ptype = make_process_type('Extranjería', 'extranjeria')
        client = make_client(manager=manager_user)
        process = make_process(client, ptype)
        api_client.force_authenticate(user=admin_user)

        response = api_client.post(
            reverse('processes:process-add-step', kwargs={'pk': process.pk}),
            {'name': 'Revisión inicial', 'description': 'Chequear documentación', 'order': 1},
            format='json',
        )

        assert response.status_code == 201
        step = ProcessStep.objects.get(pk=response.data['id'])
        assert step.process == process
        assert step.name == 'Revisión inicial'
        assert step.order == 1


@pytest.mark.django_db
class TestProcessTypeViewSet:
    def test_admin_sees_all_types(self, api_client, admin_user):
        make_process_type('Activo', 'marcas', is_active=True)
        make_process_type('Inactivo', 'marcas', is_active=False)
        api_client.force_authenticate(user=admin_user)

        response = api_client.get(reverse('processes:process-type-list'))
        assert response.status_code == 200
        assert len(response.data['results']) == 2

    def test_operator_does_not_see_inactive_types(self, api_client, operator_user):
        make_process_type('Activo', 'marcas', is_active=True)
        make_process_type('Inactivo', 'marcas', is_active=False)
        api_client.force_authenticate(user=operator_user)

        response = api_client.get(reverse('processes:process-type-list'))
        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['is_active'] is True
