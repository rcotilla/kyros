"""
Tests for the documents DRF API (DocumentViewSet).

Covers ownership scoping, forced owner on create, DRF extension
validation, and the client/process serializer helpers.
"""

import pytest

from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.documents.models import Document

from conftest import (
    make_user, make_client, make_process_type, make_process,
)


@pytest.fixture
def api_client():
    return APIClient()


def _make_doc(owner, filename='doc.pdf', title='Doc'):
    return Document.objects.create(
        owner=owner,
        title=title,
        file=SimpleUploadedFile(filename, b'%PDF-1.4 body', 'application/pdf'),
    )


@pytest.mark.django_db
class TestDocumentViewSetScope:
    """Document.get_queryset() only returns documents owned by the user."""

    def test_list_only_owned(self, api_client, manager_user, other_manager):
        _make_doc(manager_user, title='Mi doc')
        _make_doc(other_manager, title='Doc ajeno')
        api_client.force_authenticate(user=manager_user)

        response = api_client.get(reverse('documents:document-list'))
        assert response.status_code == 200
        # Paginated response
        assert response.data['results'][0]['title'] == 'Mi doc'
        assert len(response.data['results']) == 1

    def test_detail_other_users_doc_404(self, api_client, manager_user, other_manager):
        other_doc = _make_doc(other_manager, title='Doc ajeno')
        api_client.force_authenticate(user=manager_user)

        response = api_client.get(
            reverse('documents:document-detail', kwargs={'pk': other_doc.pk})
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestMyDocuments:
    """The my_documents action returns owned docs WITHOUT pagination."""

    def test_returns_all_owned_not_paginated(self, api_client, manager_user, other_manager):
        _make_doc(manager_user, title='A1')
        _make_doc(manager_user, title='A2')
        _make_doc(other_manager, title='B')
        api_client.force_authenticate(user=manager_user)

        response = api_client.get(reverse('documents:document-my-documents'))
        assert response.status_code == 200
        # my_documents returns a plain list, not a paginated dict.
        assert isinstance(response.data, list)
        assert len(response.data) == 2


@pytest.mark.django_db
class TestPerformCreateForcesOwner:
    """perform_create() overrides any attempted owner in the payload."""

    def test_owner_is_current_user_even_if_payload_has_other(self, api_client, manager_user, other_manager):
        api_client.force_authenticate(user=manager_user)
        payload = {
            'title': 'Intento de usurpación',
            'owner': other_manager.pk,  # attempt to assign to another user
            'file': SimpleUploadedFile('doc.pdf', b'%PDF-1.4', 'application/pdf'),
        }
        response = api_client.post(
            reverse('documents:document-list'), payload, format='multipart',
        )
        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)
        created = Document.objects.get(title='Intento de usurpación')
        assert created.owner == manager_user
        assert created.owner != other_manager


@pytest.mark.django_db
class TestDocumentExtensionValidation:
    """The DRF serializer enforces FileExtensionValidator (400 on .exe)."""

    def test_invalid_extension_400(self, api_client, manager_user):
        api_client.force_authenticate(user=manager_user)
        payload = {
            'title': 'Archivo peligroso',
            'file': SimpleUploadedFile('malware.exe', b'MZ', 'application/octet-stream'),
        }
        response = api_client.post(
            reverse('documents:document-list'), payload, format='multipart',
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestDocumentSerializerHelpers:
    """DocumentSerializer client_name / process_number serializer fields."""

    def _detail_doc(self, api_client, user, doc):
        api_client.force_authenticate(user=user)
        return api_client.get(
            reverse('documents:document-detail', kwargs={'pk': doc.pk})
        )

    def test_with_client_and_process(self, api_client, manager_user, operator_user):
        client = make_client(manager=manager_user,
                             first_name='Ana', last_name='Lopez')
        ptype = make_process_type('Extranjería', 'extranjeria')
        process = make_process(client, ptype)
        doc = Document.objects.create(
            owner=operator_user, title='Doc', client=client, process=process,
            file=SimpleUploadedFile('doc.pdf', b'%PDF', 'application/pdf'),
        )
        response = self._detail_doc(api_client, operator_user, doc)
        assert response.status_code == 200
        assert response.data['client_name'] == 'Ana Lopez'
        assert response.data['process_number'] == process.file_number

    def test_without_client_or_process(self, api_client, operator_user):
        doc = _make_doc(operator_user, title='Huérfano')
        response = self._detail_doc(api_client, operator_user, doc)
        assert response.status_code == 200
        assert response.data['client_name'] is None
        assert response.data['process_number'] is None
