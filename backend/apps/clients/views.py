"""Views for clients app."""

from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Client
from .serializers import (
    ClientListSerializer,
    ClientDetailSerializer,
    ClientCreateUpdateSerializer,
)


class ClientViewSet(viewsets.ModelViewSet):
    """
    API endpoint for clients.

    Provides CRUD operations with role-based filtering:
    - Gestores see all clients
    - Operators see assigned clients
    - Clients see only their own data
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'first_name', 'last_name', 'document_number',
        'email', 'phone', 'notes'
    ]
    ordering_fields = ['created_at', 'last_name', 'first_name']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        # Gestores and admins see all clients
        if hasattr(user, 'profile') and user.profile.role.name in ('admin', 'manager'):
            return Client.objects.all()
        # Others see only assigned clients
        return Client.objects.filter(
            Q(assigned_to=user) | Q(created_by=user)
        ).distinct()

    def get_serializer_class(self):
        if self.action == 'list':
            return ClientListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return ClientCreateUpdateSerializer
        return ClientDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def my_clients(self, request):
        """List clients assigned to the current user."""
        clients = Client.objects.filter(assigned_to=request.user)
        serializer = ClientListSerializer(clients, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def processes(self, request, pk=None):
        """List processes for a specific client."""
        client = self.get_object()
        from apps.processes.serializers import ProcessListSerializer
        processes = client.processes.all()
        serializer = ProcessListSerializer(processes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """List documents for a specific client."""
        client = self.get_object()
        from apps.documents.serializers import DocumentSerializer
        documents = client.documents.all()
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        """Generate PDF report for this client."""
        from django.http import HttpResponse
        from docgen.services.pdf_generator import generate_client_report, WEASYPRINT_AVAILABLE

        if not WEASYPRINT_AVAILABLE:
            return Response(
                {'error': 'WeasyPrint no está instalado'},
                status=503
            )

        client = self.get_object()
        pdf_path = generate_client_report(client)

        with open(pdf_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            filename = f"cliente_{client.document_number}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
