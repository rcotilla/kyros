"""
Tests for panel views (gestor workflows, authorization, step management).

Uses django.test.Client + force_login, hitting real templates.
"""

import pytest

from django.urls import reverse

from apps.clients.models import Client
from apps.processes.models import (
    Process, ProcessStep, ProcessTemplate, ProcessTemplateStep, ProcessType,
)

from conftest import (
    make_process_type, make_client, make_process,
)


@pytest.mark.django_db
class TestGestorAuthorization:
    """GestorRequiredMixin + login_required behavior."""

    def test_manager_sees_home(self, client, manager_user):
        client.force_login(manager_user)
        response = client.get(reverse('panel:home'))
        assert response.status_code == 200

    def test_operator_redirected_from_gestor_view(self, client, operator_user):
        client.force_login(operator_user)
        response = client.get(reverse('panel:gestor_clients'))
        assert response.status_code == 302
        assert response.url == reverse('landing:home')

    def test_anonymous_redirected_from_gestor_view(self, client):
        # login_required(login_url='/') sends anonymous users to '/?next=...'
        response = client.get(reverse('panel:gestor_clients'))
        assert response.status_code == 302
        # The login_url is '/', and Django appends '?next=<original path>'
        assert response.url.split('?')[0] == reverse('landing:home')


@pytest.mark.django_db
class TestGestorClientCreateView:
    def test_post_creates_client_with_creator(self, client, manager_user):
        client.force_login(manager_user)
        data = {
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'document_type': 'dni',
            'document_number': 'DNI-30111222',
            'country': 'AR',
        }
        response = client.post(reverse('panel:gestor_client_create'), data)

        assert response.status_code == 302
        assert response.url == reverse('panel:gestor_clients')
        created = Client.objects.get(document_number='DNI-30111222')
        assert created.first_name == 'Juan'
        assert created.created_by == manager_user


@pytest.mark.django_db
class TestGestorProcessCreateView:
    def _setup(self, manager_user):
        ptype = make_process_type('Extranjería', 'extranjeria')
        client = make_client(manager=manager_user)
        template = ProcessTemplate.objects.create(
            name='Plantilla 1', process_type=ptype,
        )
        ProcessTemplateStep.objects.create(
            template=template, name='Paso A', order=1,
        )
        return ptype, client, template

    def test_post_creates_process_and_applies_template(self, client, manager_user):
        client.force_login(manager_user)
        ptype, client_obj, template = self._setup(manager_user)

        response = client.post(reverse('panel:gestor_process_create'), {
            'title': 'Trámite de residencia',
            'process_type': ptype.pk,
            'client': client_obj.pk,
            'status': 'draft',
            'priority': 'medium',
            'template': template.pk,
        })

        assert response.status_code == 302
        process = Process.objects.get(title='Trámite de residencia')
        assert response.url == reverse('panel:gestor_process_detail', kwargs={'pk': process.pk})
        assert process.file_number.startswith('EXP-')
        assert process.gestor == manager_user
        assert process.steps.count() == 1
        assert process.steps.first().name == 'Paso A'


@pytest.mark.django_db
class TestGestorProcessAddStepView:
    def test_add_step_with_explicit_order_shifts_existing(self, client, manager_user):
        client.force_login(manager_user)
        ptype = make_process_type('Extranjería', 'extranjeria')
        client_obj = make_client(manager=manager_user)
        process = make_process(client_obj, ptype)
        ProcessStep.objects.create(process=process, name='Uno', order=1)
        ProcessStep.objects.create(process=process, name='Dos', order=2)

        response = client.post(
            reverse('panel:gestor_process_add_step', kwargs={'pk': process.pk}),
            {'name': 'Nuevo', 'order': '2', 'status': 'pending'},
        )

        assert response.status_code == 302
        steps = process.steps.all().order_by('order')
        orders = [s.order for s in steps]
        assert orders == [1, 2, 3]
        assert steps.get(name='Dos').order == 3
        assert steps.get(name='Nuevo').order == 2


@pytest.mark.django_db
class TestGestorProcessDeleteStepView:
    def test_delete_step_reorders_remaining(self, client, manager_user):
        client.force_login(manager_user)
        ptype = make_process_type('Extranjería', 'extranjeria')
        client_obj = make_client(manager=manager_user)
        process = make_process(client_obj, ptype)
        s1 = ProcessStep.objects.create(process=process, name='Uno', order=1)
        ProcessStep.objects.create(process=process, name='Dos', order=2)
        ProcessStep.objects.create(process=process, name='Tres', order=3)

        response = client.post(
            reverse(
                'panel:gestor_process_delete_step',
                kwargs={'process_pk': process.pk, 'step_pk': s1.pk},
            ),
        )

        assert response.status_code == 302
        steps = process.steps.all().order_by('order')
        assert list(steps.values_list('name', 'order')) == [
            ('Dos', 1),
            ('Tres', 2),
        ]


@pytest.mark.django_db
class TestGestorClientEditView:
    def test_deactivate_action_sets_status_inactive(self, client, manager_user):
        client.force_login(manager_user)
        client_obj = make_client(manager=manager_user)

        response = client.post(
            reverse('panel:gestor_client_edit', kwargs={'pk': client_obj.pk}),
            {'action': 'deactivate'},
        )

        assert response.status_code == 302
        assert response.url == reverse('panel:gestor_clients')
        client_obj.refresh_from_db()
        assert client_obj.status == 'inactive'
