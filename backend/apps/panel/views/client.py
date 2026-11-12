"""
Client views — sees their own processes and documents.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from apps.clients.models import Client
from apps.processes.models import Process


@method_decorator(login_required(login_url='/'), name='dispatch')
class ClientHomeView(View):
    """Client view — their processes and documents."""

    def get(self, request):
        user = request.user
        try:
            client = Client.objects.get(email=user.email)
        except (Client.DoesNotExist, Client.MultipleObjectsReturned):
            # MultipleObjectsReturned happens when several Client rows share the
            # same email (e.g. two empty '' emails); it is not a subclass of
            # DoesNotExist, so it must be caught explicitly to avoid a 500.
            client = None

        processes = []
        documents = []
        if client:
            processes = client.processes.select_related('process_type', 'gestor').order_by('-created_at')
            documents = client.documents.all()

        return render(request, 'panel/client/home.html', {
            'client': client,
            'processes': processes,
            'documents': documents,
        })


@method_decorator(login_required(login_url='/'), name='dispatch')
class ClientProcessDetailView(View):
    """View a process detail (client, read-only)."""

    def get(self, request, pk):
        user = request.user
        process = get_object_or_404(
            Process.objects.select_related('client', 'process_type', 'gestor'),
            pk=pk
        )
        if process.client.email != user.email:
            messages.error(request, _('No tenés acceso a este proceso.'))
            return redirect('panel:client_home')

        steps = process.steps.all().order_by('order')
        documents = process.documents.all()

        return render(request, 'panel/client/process_detail.html', {
            'process': process,
            'steps': steps,
            'documents': documents,
        })


@method_decorator(login_required(login_url='/'), name='dispatch')
class ClientProfileView(View):
    """Client profile view."""

    def get(self, request):
        user = request.user
        try:
            client = Client.objects.get(email=user.email)
        except (Client.DoesNotExist, Client.MultipleObjectsReturned):
            # MultipleObjectsReturned happens when several Client rows share the
            # same email (e.g. two empty '' emails); it is not a subclass of
            # DoesNotExist, so it must be caught explicitly to avoid a 500.
            client = None

        return render(request, 'panel/client/profile.html', {
            'client': client,
        })
