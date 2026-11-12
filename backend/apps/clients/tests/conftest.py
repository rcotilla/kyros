"""
Fixtures for the clients app tests.

Uses the shared factory helpers from the root conftest.py (make_user,
make_client, etc.) and defines client-specific fixtures.
"""

import pytest

from apps.clients.models import Client


@pytest.fixture
def client(db):
    """A Client instance with test data."""
    return Client.objects.create(
        first_name='Juan',
        last_name='Perez',
        document_type='dni',
        document_number='12345678',
        email='juan@example.com',
        phone='+54 11 1234-5678',
        country='AR',
        status='active',
    )


@pytest.fixture
def assigned_client(db, operator_user):
    """A Client assigned to the operator user."""
    return Client.objects.create(
        first_name='Maria',
        last_name='Gonzalez',
        document_type='dni',
        document_number='87654321',
        email='maria@example.com',
        phone='+54 11 9876-5432',
        country='AR',
        status='active',
        assigned_to=operator_user,
    )
