"""
Tests for the documents models (Document, path helpers).

Reflects the ACTUAL current behavior of the models, including known
limitations (model-level validation does not run FileExtensionValidator).
"""

import pytest

from django.core.files.uploadedfile import SimpleUploadedFile

from apps.documents.models import Document
from apps.documents.models.uploaded import _safe_slug, document_upload_path

from conftest import (
    make_user, make_client, make_process_type, make_process,
)


@pytest.mark.django_db
class TestDocumentSaveFileSize:
    """Document.save() computes file_size from the uploaded file."""

    def test_file_size_matches_content_length(self, operator_user):
        doc = Document.objects.create(
            owner=operator_user,
            title='Contrato',
            file=SimpleUploadedFile(
                name='doc.pdf',
                content=b'%PDF-1.4 ...content...',
                content_type='application/pdf',
            ),
        )
        doc.refresh_from_db()
        assert doc.file_size == len(b'%PDF-1.4 ...content...')


@pytest.mark.django_db
class TestSafeSlug:
    """_safe_slug normalizes names/paths into filesystem-safe slugs."""

    def test_normalizes_accents_and_spaces(self):
        assert _safe_slug('José Pérez') == 'Jose_Perez'

    def test_empty_returns_sin_asignar(self):
        assert _safe_slug('') == 'sin_asignar'
        assert _safe_slug(None) == 'sin_asignar'


@pytest.mark.django_db
class TestDocumentUploadPath:
    """document_upload_path builds documents/<client>/<type>/<file>/<file>."""

    def test_full_path(self, operator_user, manager_user):
        client = make_client(manager=manager_user,
                             first_name='José', last_name='Pérez')
        ptype = make_process_type('Extranjería', 'extranjeria')
        process = make_process(client, ptype, file_number='EXP-00001')
        doc = Document.objects.create(
            owner=operator_user,
            title='Doc',
            client=client,
            process=process,
            file=SimpleUploadedFile('archivo.pdf', b'%PDF', 'application/pdf'),
        )
        upload_to = Document._meta.get_field('file').upload_to
        path = upload_to(doc, 'archivo.pdf')
        assert path == 'documents/Jose_Perez/Extranjeria/EXP-00001/archivo.pdf'

    def test_without_client_and_process_uses_fallbacks(self, operator_user):
        doc = Document.objects.create(
            owner=operator_user,
            title='Doc',
            file=SimpleUploadedFile('archivo.pdf', b'%PDF', 'application/pdf'),
        )
        upload_to = Document._meta.get_field('file').upload_to
        path = upload_to(doc, 'archivo.pdf')
        assert path == 'documents/sin_cliente/sin_tipo/sin_expediente/archivo.pdf'


@pytest.mark.django_db
class TestDocumentInvalidExtension:
    """Model-level save does NOT reject invalid extensions.

    The FileExtensionValidator is defined on the `file` field, but Django
    only runs model validators during full_clean()/form/DRF validation.
    Direct objects.create()/save() bypasses them, so a .exe file is
    accepted at the model layer. This is expected behavior — not a bug.
    """

    def test_save_accepts_exe_at_model_level(self, operator_user):
        doc = Document.objects.create(
            owner=operator_user,
            title='Ejecutable',
            file=SimpleUploadedFile('malware.exe', b'MZ', 'application/octet-stream'),
        )
        assert doc.pk is not None
        # Django appends a random suffix to avoid collisions, so check only
        # that the original extension (.exe) was preserved after upload_to.
        assert doc.file.name.endswith('.exe')



