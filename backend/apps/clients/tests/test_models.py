"""
Tests for the Client model.
"""

import pytest

from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.clients.models import Client


@pytest.mark.django_db
class TestClientModel:
    """Basic Client model behavior."""

    def test_create_client_with_minimal_data(self):
        """Create a client with only required fields."""
        client = Client.objects.create(
            first_name='Carlos',
            last_name='Lopez',
            document_type='dni',
            document_number='11111111',
        )
        assert client.pk is not None
        assert client.first_name == 'Carlos'
        assert client.last_name == 'Lopez'
        assert client.document_type == 'dni'
        assert client.document_number == '11111111'

    def test_full_name_property(self):
        """full_name returns 'first_name last_name'."""
        client = Client(
            first_name='Ana',
            last_name='Martinez',
            document_type='dni',
            document_number='22222222',
        )
        assert client.full_name == 'Ana Martinez'

    def test_document_number_unique(self):
        """Cannot create two clients with the same document_number."""
        Client.objects.create(
            first_name='One',
            last_name='Test',
            document_type='dni',
            document_number='33333333',
        )
        with pytest.raises(IntegrityError):
            Client.objects.create(
                first_name='Two',
                last_name='Test',
                document_type='dni',
                document_number='33333333',
            )

    def test_document_number_case_insensitive(self):
        """Model-level unique constraint is case-sensitive.

        The case-insensitive uniqueness is enforced at the serializer level
        (ClientCreateUpdateSerializer.validate_document_number), not at the
        model level. This test documents the actual model behavior.
        """
        Client.objects.create(
            first_name='Upper',
            last_name='Case',
            document_type='dni',
            document_number='ABC123',
        )
        # Model allows 'abc123' as a separate record (case-sensitive unique)
        client2 = Client.objects.create(
            first_name='Lower',
            last_name='Case',
            document_type='dni',
            document_number='abc123',
        )
        assert client2.pk is not None
        assert Client.objects.filter(document_number__iexact='abc123').count() == 2

    def test_phone_regex_valid(self, admin_user):
        """Valid phone numbers pass the regex validator."""
        client = Client(
            first_name='Test',
            last_name='Phone',
            document_type='dni',
            document_number='44444444',
            phone='+54 11 1234-5678',
            created_by=admin_user,
        )
        # full_clean runs validators
        client.full_clean()
        assert client.phone == '+54 11 1234-5678'

    def test_phone_regex_invalid(self):
        """Invalid phone numbers raise ValidationError."""
        client = Client(
            first_name='Test',
            last_name='Phone',
            document_type='dni',
            document_number='55555555',
            phone='not-a-phone',
        )
        with pytest.raises(ValidationError):
            client.full_clean()

    def test_status_default_is_active(self):
        """Default status is 'active'."""
        client = Client.objects.create(
            first_name='Default',
            last_name='Status',
            document_type='dni',
            document_number='66666666',
        )
        assert client.status == 'active'

    def test_country_default_is_ar(self):
        """Default country is 'AR'."""
        client = Client.objects.create(
            first_name='Default',
            last_name='Country',
            document_type='dni',
            document_number='77777777',
        )
        assert client.country == 'AR'

    def test_str_representation(self):
        """__str__ returns 'Nombre Apellido (documento)'."""
        client = Client(
            first_name='Juan',
            last_name='Perez',
            document_type='dni',
            document_number='12345678',
        )
        assert str(client) == 'Juan Perez (12345678)'

    def test_assigned_to_set_null_on_user_delete(self):
        """When assigned user is deleted, assigned_to becomes NULL."""
        from conftest import make_user

        user = make_user('temp_user', 'operator')
        client = Client.objects.create(
            first_name='Assigned',
            last_name='User',
            document_type='dni',
            document_number='88888888',
            assigned_to=user,
        )
        assert client.assigned_to == user

        user.delete()
        client.refresh_from_db()
        assert client.assigned_to is None
