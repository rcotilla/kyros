"""
Tests for the tasks DRF API (TaskViewSet).

Covers the assigned_to/created_by queryset scope, the (un-validated)
created_by forge behavior, search/ordering, and pagination.
"""

import pytest

from datetime import timedelta

from rest_framework.test import APIClient
from django.urls import reverse
from django.utils import timezone

from apps.tasks.models import Task

from conftest import make_user


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestTaskViewSetScope:
    """get_queryset() returns tasks assigned to OR created by the user."""

    def _setup(self, manager, operator, other_manager):
        task_a = Task.objects.create(
            title='Tarea A', description='desc A',
            created_by=manager, assigned_to=operator,
        )
        task_b = Task.objects.create(
            title='Tarea B', description='desc B', created_by=other_manager,
        )
        return task_a, task_b

    def test_manager_sees_tasks_they_created(self, api_client, manager_user, operator_user, other_manager):
        task_a, task_b = self._setup(manager_user, operator_user, other_manager)
        api_client.force_authenticate(user=manager_user)

        response = api_client.get(reverse('tasks:task-list'))
        assert response.status_code == 200
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['id'] == task_a.pk

    def test_operator_sees_tasks_assigned_to_them(self, api_client, manager_user, operator_user, other_manager):
        task_a, task_b = self._setup(manager_user, operator_user, other_manager)
        api_client.force_authenticate(user=operator_user)

        response = api_client.get(reverse('tasks:task-list'))
        assert response.status_code == 200
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['id'] == task_a.pk

    def test_other_manager_sees_only_their_own_task(self, api_client, manager_user, operator_user, other_manager):
        """other_manager neither created nor is assigned task A, so only task B."""
        task_a, task_b = self._setup(manager_user, operator_user, other_manager)
        api_client.force_authenticate(user=other_manager)

        response = api_client.get(reverse('tasks:task-list'))
        assert response.status_code == 200
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['id'] == task_b.pk


@pytest.mark.django_db
class TestTaskForgeCreatedBy:
    """POST does NOT force created_by to the authenticated user.

    There is no perform_create() override in TaskViewSet, and the
    serializer exposes `created_by` as a writable field. A caller can
    therefore create a task attributed to ANOTHER user. This reflects
    the current behavior and is a defect worth documenting.
    """

    def test_created_by_is_forced_to_authenticated_user(
        self, api_client, manager_user, other_manager
    ):
        """created_by cannot be forged via the payload.

        created_by is read-only in the serializer and TaskViewSet.perform_create
        forces it to the authenticated user, so a client cannot attribute a task
        to someone else.
        """
        api_client.force_authenticate(user=manager_user)
        payload = {
            'title': 'Tarea forjada',
            'description': 'desc',
            'created_by': other_manager.pk,  # attempt to attribute to another user
        }
        response = api_client.post(
            reverse('tasks:task-list'), payload, format='json',
        )
        assert response.status_code in (201, 200)
        task = Task.objects.get(title='Tarea forjada')
        assert task.created_by == manager_user
        assert task.created_by != other_manager


@pytest.mark.django_db
class TestTaskSearchAndOrdering:
    """SearchFilter on title/description and OrderingFilter on due_date."""

    def test_search_filters_by_title(self, api_client, manager_user):
        Task.objects.create(title='Residencia', description='d1', created_by=manager_user)
        Task.objects.create(title='Pasaporte', description='d2', created_by=manager_user)
        api_client.force_authenticate(user=manager_user)

        response = api_client.get(reverse('tasks:task-list'), {'search': 'Residencia'})
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['title'] == 'Residencia'

    def test_ordering_by_due_date(self, api_client, manager_user):
        Task.objects.create(
            title='Primera', description='d', created_by=manager_user,
            due_date=timezone.now() + timedelta(days=2),
        )
        Task.objects.create(
            title='Segunda', description='d', created_by=manager_user,
            due_date=timezone.now() + timedelta(days=1),
        )
        api_client.force_authenticate(user=manager_user)

        response = api_client.get(reverse('tasks:task-list'), {'ordering': 'due_date'})
        results = response.data['results']
        assert [r['title'] for r in results] == ['Segunda', 'Primera']


@pytest.mark.django_db
class TestTaskPagination:
    """The list endpoint returns a paginated dict, not a plain list."""

    def test_list_is_paginated(self, api_client, manager_user):
        Task.objects.create(title='Tarea', description='d', created_by=manager_user)
        api_client.force_authenticate(user=manager_user)

        response = api_client.get(reverse('tasks:task-list'))
        assert response.status_code == 200
        assert 'count' in response.data
        assert 'results' in response.data
        assert response.data['count'] == 1
