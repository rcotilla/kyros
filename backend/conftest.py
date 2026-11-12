"""
Global pytest fixtures and factory helpers for the KAIROS test suite.

Conventions:
  - Roles: 'admin', 'manager', 'operator', 'client' (see apps.core.models.Role).
  - Every user with a role MUST have a UserProfile (related_name='profile').
  - Tests that touch the DB are wrapped in @pytest.mark.django_db.
"""

import pytest

from django.contrib.auth.models import User

from apps.core.models import Role, UserProfile
from apps.clients.models import Client
from apps.processes.models import (
    Process, ProcessType, ProcessTemplate, ProcessTemplateStep, ProcessStep,
)


# ---------------------------------------------------------------------------
# Factory helpers (plain functions, no external deps)
# ---------------------------------------------------------------------------

def make_role(name):
    """Return (creating if needed) the Role with the given name."""
    role, _ = Role.objects.get_or_create(name=name)
    return role


def make_user(username, role_name, password='pass1234', is_staff=False):
    """Create a User + UserProfile with the given role. Returns the user."""
    user = User.objects.create_user(
        username=username, password=password, is_staff=is_staff,
    )
    role = make_role(role_name)
    UserProfile.objects.create(user=user, role=role)
    return user


def make_process_type(name, category='otro', is_active=True):
    """Create a ProcessType."""
    return ProcessType.objects.create(
        name=name, category=category, is_active=is_active,
    )


def make_client(manager=None, **kwargs):
    """Create a Client, defaulting required fields to sensible values."""
    data = {
        'first_name': kwargs.pop('first_name', 'Test'),
        'last_name': kwargs.pop('last_name', 'Client'),
        'document_type': kwargs.pop('document_type', 'dni'),
        'document_number': kwargs.pop(
            'document_number', f'DNI-{Client.objects.count() + 1}'
        ),
        'country': kwargs.pop('country', 'AR'),
    }
    data.update(kwargs)
    if manager is not None:
        data['assigned_to'] = manager
    return Client.objects.create(**data)


def make_process(client, process_type, **kwargs):
    """Create a Process linked to the given client/process_type."""
    data = {
        'title': kwargs.pop('title', f'Process {Process.objects.count() + 1}'),
        'client': client,
        'process_type': process_type,
    }
    data.update(kwargs)
    return Process.objects.create(**data)


# ---------------------------------------------------------------------------
# Role fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def role():
    """A 'manager' Role instance."""
    return make_role('manager')


@pytest.fixture
def admin_user(db):
    return make_user('admin_user', 'admin', is_staff=True)


@pytest.fixture
def manager_user(db):
    return make_user('manager_user', 'manager')


@pytest.fixture
def operator_user(db):
    return make_user('operator_user', 'operator')


@pytest.fixture
def client_user(db):
    return make_user('client_user', 'client')


@pytest.fixture
def other_manager(db):
    """A second manager, useful for scope tests."""
    return make_user('manager_2', 'manager')
