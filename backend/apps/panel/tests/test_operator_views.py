"""
Tests for the panel operator views (OperatorHomeView, OperatorTaskDetailView).

Uses django.test.Client + force_login.
"""

import pytest

from django.urls import reverse
from django.utils import timezone

from apps.tasks.models import Task

from conftest import make_user


@pytest.mark.django_db
class TestOperatorHomeView:
    """Only operators can access panel:operator_home."""

    def test_operator_sees_home(self, client, operator_user):
        client.force_login(operator_user)
        response = client.get(reverse('panel:operator_home'))
        assert response.status_code == 200

    def test_manager_redirected(self, client, manager_user):
        client.force_login(manager_user)
        response = client.get(reverse('panel:operator_home'))
        assert response.status_code == 302
        assert response.url == reverse('landing:home')


@pytest.mark.django_db
class TestOperatorTaskDetailGet:
    """Operator can view a task only if it is assigned to them."""

    def test_operator_sees_assigned_task(self, client, operator_user, manager_user):
        task = Task.objects.create(
            title='Tarea', description='d',
            created_by=manager_user, assigned_to=operator_user,
        )
        client.force_login(operator_user)
        response = client.get(
            reverse('panel:operator_task_detail', kwargs={'pk': task.pk})
        )
        assert response.status_code == 200

    def test_unassigned_task_404(self, client, operator_user, manager_user):
        task = Task.objects.create(
            title='Tarea', description='d', created_by=manager_user,
        )
        client.force_login(operator_user)
        response = client.get(
            reverse('panel:operator_task_detail', kwargs={'pk': task.pk})
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestOperatorTaskDetailPost:
    """POST updates task status; completed_at set only on 'completed'.

    Documented behavior: when a task is moved back to a non-completed
    status, completed_at is NOT cleared (stale). The POST handler also
    does not re-check the operator role — it only checks assigned_to.
    """

    def test_completed_sets_completed_at(self, client, operator_user, manager_user):
        task = Task.objects.create(
            title='Tarea', description='d',
            created_by=manager_user, assigned_to=operator_user,
        )
        client.force_login(operator_user)
        response = client.post(
            reverse('panel:operator_task_detail', kwargs={'pk': task.pk}),
            {'status': 'completed'},
        )
        assert response.status_code == 302
        assert response.url == reverse('panel:operator_task_detail', kwargs={'pk': task.pk})
        task.refresh_from_db()
        assert task.status == 'completed'
        assert task.completed_at is not None

    def test_pending_after_completed_clears_completed_at(
        self, client, operator_user, manager_user
    ):
        """Moving back to 'pending' clears the completed_at timestamp."""
        task = Task.objects.create(
            title='Tarea', description='d',
            created_by=manager_user, assigned_to=operator_user,
            status='completed',
        )
        task.completed_at = timezone.now()
        task.save()
        client.force_login(operator_user)
        response = client.post(
            reverse('panel:operator_task_detail', kwargs={'pk': task.pk}),
            {'status': 'pending'},
        )
        assert response.status_code == 302
        task.refresh_from_db()
        assert task.status == 'pending'
        # completed_at is cleared when leaving the completed state.
        assert task.completed_at is None

    def test_invalid_status_does_not_change(self, client, operator_user, manager_user):
        task = Task.objects.create(
            title='Tarea', description='d',
            created_by=manager_user, assigned_to=operator_user,
            status='pending',
        )
        client.force_login(operator_user)
        response = client.post(
            reverse('panel:operator_task_detail', kwargs={'pk': task.pk}),
            {'status': 'no-existe'},
        )
        assert response.status_code == 302
        task.refresh_from_db()
        assert task.status == 'pending'

    def test_unassigned_task_404_on_post(self, client, operator_user, manager_user):
        task = Task.objects.create(
            title='Tarea', description='d', created_by=manager_user,
        )
        client.force_login(operator_user)
        response = client.post(
            reverse('panel:operator_task_detail', kwargs={'pk': task.pk}),
            {'status': 'completed'},
        )
        assert response.status_code == 404

    def test_non_operator_cannot_update_assigned_task_on_post(
        self, client, manager_user, operator_user
    ):
        """POST re-checks the operator role.

        A manager assigned to the task cannot mutate it; the POST branch does
        its own role check and redirects away before any state change.
        """
        task = Task.objects.create(
            title='Tarea del operador', description='d',
            created_by=manager_user, assigned_to=operator_user,
            status='pending',
        )
        client.force_login(manager_user)
        response = client.post(
            reverse('panel:operator_task_detail', kwargs={'pk': task.pk}),
            {'status': 'completed'},
        )
        assert response.status_code == 302
        assert response.url.startswith(reverse('landing:home'))
        task.refresh_from_db()
        assert task.status == 'pending'
        assert task.completed_at is None
