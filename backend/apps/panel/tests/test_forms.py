"""
Tests for panel forms (ClientForm, ProcessForm, DocumentUploadForm).
"""

import pytest

from django.core.files.uploadedfile import SimpleUploadedFile

from apps.panel.forms import ClientForm, ProcessForm, DocumentUploadForm
from apps.processes.models import ProcessTemplate

from conftest import make_process_type, make_client


VALID_CLIENT = {
    'first_name': 'Ana',
    'last_name': 'Gómez',
    'document_type': 'dni',
    'document_number': 'DNI-30111999',
    'country': 'AR',
}


@pytest.mark.django_db
class TestClientForm:
    def test_duplicate_document_number_is_invalid(self):
        make_client(document_number='DNI-55551111')
        form = ClientForm(data={**VALID_CLIENT, 'document_number': 'DNI-55551111'})
        assert not form.is_valid()
        assert 'document_number' in form.errors

    def test_invalid_phone_is_invalid(self):
        form = ClientForm(data={**VALID_CLIENT, 'phone': 'abc'})
        assert not form.is_valid()
        assert 'phone' in form.errors

    def test_valid_phone_is_valid(self):
        form = ClientForm(data={**VALID_CLIENT, 'phone': '+54 11 1234-5678'})
        assert form.is_valid()

    def test_valid_data_is_valid(self):
        form = ClientForm(data=VALID_CLIENT)
        assert form.is_valid()


@pytest.mark.django_db
class TestProcessForm:
    def _make_template(self, ptype, is_active):
        return ProcessTemplate.objects.create(
            name='Tpl', process_type=ptype, is_active=is_active,
        )

    def test_template_field_present(self):
        form = ProcessForm()
        assert 'template' in form.fields

    def test_active_template_in_queryset(self):
        ptype = make_process_type('Extranjería', 'extranjeria')
        self._make_template(ptype, is_active=True)
        form = ProcessForm()
        assert form.fields['template'].queryset.count() == 1

    def test_inactive_template_not_in_queryset(self):
        ptype = make_process_type('Extranjería', 'extranjeria')
        self._make_template(ptype, is_active=False)
        form = ProcessForm()
        assert form.fields['template'].queryset.count() == 0


@pytest.mark.django_db
class TestDocumentUploadForm:
    def test_exe_file_is_invalid(self):
        data = {
            'title': 'Instalador',
            'doc_type': 'evidence',
        }
        files = {
            'file': SimpleUploadedFile('setup.exe', b'fake-binary', content_type='application/octet-stream'),
        }
        form = DocumentUploadForm(data=data, files=files)
        assert not form.is_valid()
        assert 'file' in form.errors

    def test_pdf_file_is_valid(self):
        data = {
            'title': 'Contrato',
            'doc_type': 'contract',
        }
        files = {
            'file': SimpleUploadedFile('contrato.pdf', b'%PDF-1.4', content_type='application/pdf'),
        }
        form = DocumentUploadForm(data=data, files=files)
        assert form.is_valid()
