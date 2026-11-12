"""
Tests for the clients serializers.
"""

import pytest

from apps.clients.models import Client
from apps.clients.serializers import (
    ClientListSerializer,
    ClientDetailSerializer,
    ClientCreateUpdateSerializer,
)


@pytest.mark.django_db
class TestClientListSerializer:
    """ClientListSerializer returns compact fields."""

    def test_list_serializer_fields(self, client):
        """Returns only the compact set of fields."""
        serializer = ClientListSerializer(client)
        data = serializer.data

        expected_fields = {
            'id', 'full_name', 'document_type', 'document_number',
            'email', 'phone', 'status', 'assigned_to', 'created_at',
        }
        assert set(data.keys()) == expected_fields
        assert data['full_name'] == 'Juan Perez'
        assert data['document_number'] == '12345678'


@pytest.mark.django_db
class TestClientDetailSerializer:
    """ClientDetailSerializer includes full info and counts."""

    def test_detail_serializer_includes_counts(self, client):
        """Includes processes_count and documents_count fields."""
        serializer = ClientDetailSerializer(client)
        data = serializer.data

        assert 'processes_count' in data
        assert 'documents_count' in data
        assert data['processes_count'] == 0
        assert data['documents_count'] == 0

    def test_detail_serializer_full_name(self, client):
        """full_name is included in detail serializer."""
        serializer = ClientDetailSerializer(client)
        assert serializer.data['full_name'] == 'Juan Perez'


@pytest.mark.django_db
class TestClientCreateUpdateSerializer:
    """ClientCreateUpdateSerializer validation."""

    def test_create_update_serializer_valid(self):
        """Valid data passes serializer validation."""
        data = {
            'first_name': 'Pedro',
            'last_name': 'Gomez',
            'document_type': 'dni',
            'document_number': '99999999',
            'country': 'AR',
        }
        serializer = ClientCreateUpdateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_create_update_serializer_duplicate_document(self):
        """Duplicate document_number raises validation error."""
        Client.objects.create(
            first_name='Existing',
            last_name='Client',
            document_type='dni',
            document_number='12345678',
        )
        data = {
            'first_name': 'New',
            'last_name': 'Client',
            'document_type': 'dni',
            'document_number': '12345678',
        }
        serializer = ClientCreateUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'document_number' in serializer.errors

    def test_create_update_serializer_duplicate_case_insensitive(self):
        """Case-insensitive duplicate document_number raises error."""
        Client.objects.create(
            first_name='Existing',
            last_name='Client',
            document_type='dni',
            document_number='ABC123',
        )
        data = {
            'first_name': 'New',
            'last_name': 'Client',
            'document_type': 'dni',
            'document_number': 'abc123',
        }
        serializer = ClientCreateUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'document_number' in serializer.errors

    def test_read_only_fields_not_editable(self):
        """created_by, created_at are read-only in detail serializer."""
        client = Client.objects.create(
            first_name='Read',
            last_name='Only',
            document_type='dni',
            document_number='11111111',
        )
        serializer = ClientDetailSerializer(client)
        assert 'created_by' in serializer.fields
        assert 'created_at' in serializer.fields
        assert serializer.fields['created_by'].read_only is True
        assert serializer.fields['created_at'].read_only is True
