"""
Tests for Process model behavior (save, templates).
"""

import pytest

from apps.processes.models import (
    Process, ProcessStep, ProcessTemplate, ProcessTemplateStep, ProcessType,
)

from conftest import make_process_type, make_client, make_process


@pytest.mark.django_db
class TestProcessSave:
    """Process.save() auto-generates the file_number when left blank."""

    def test_generates_file_number_when_blank(self):
        process_type = make_process_type('Extranjería', 'extranjeria')
        client = make_client()

        process = make_process(client, process_type, file_number='')
        process.refresh_from_db()

        assert process.file_number == 'EXP-00001'

    def test_generates_incrementing_file_number(self):
        """The second blank process gets the next number based on last.id."""
        process_type = make_process_type('Extranjería', 'extranjeria')
        client = make_client()

        first = make_process(client, process_type, file_number='')
        second = make_process(client, process_type, file_number='')
        second.refresh_from_db()

        assert first.file_number == 'EXP-00001'
        assert second.file_number == 'EXP-00002'

    def test_does_not_overwrite_explicit_file_number(self):
        process_type = make_process_type('Extranjería', 'extranjeria')
        client = make_client()

        process = make_process(client, process_type, file_number='EXP-99999')
        process.refresh_from_db()

        assert process.file_number == 'EXP-99999'


@pytest.mark.django_db
class TestProcessTemplateApply:
    """ProcessTemplate.apply_to() copies steps onto a process."""

    def test_apply_to_creates_steps_for_process(self):
        process_type = make_process_type('Extranjería', 'extranjeria')
        client = make_client()

        template = ProcessTemplate.objects.create(
            name='Plantilla Base', process_type=process_type,
        )
        ProcessTemplateStep.objects.create(
            template=template, name='Paso 1', order=1,
        )
        ProcessTemplateStep.objects.create(
            template=template, name='Paso 2', order=2,
        )

        process = make_process(client, process_type)
        count = template.apply_to(process)

        steps = ProcessStep.objects.filter(process=process).order_by('order')
        assert count == 2
        assert steps.count() == 2

        first, second = steps
        assert first.name == 'Paso 1'
        assert first.order == 1
        assert first.status == 'pending'
        assert first.due_date is None
        assert second.name == 'Paso 2'
        assert second.order == 2
        assert second.status == 'pending'
        assert second.due_date is None
