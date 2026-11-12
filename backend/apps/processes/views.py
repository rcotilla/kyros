"""Views for processes app."""

from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import ProcessType, Process, ProcessStep
from .serializers import (
    ProcessTypeSerializer,
    ProcessListSerializer,
    ProcessDetailSerializer,
    ProcessCreateUpdateSerializer,
    ProcessStepSerializer,
)


class ProcessTypeViewSet(viewsets.ModelViewSet):
    """API endpoint for process types."""
    queryset = ProcessType.objects.all()
    serializer_class = ProcessTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['category', 'name']

    def get_queryset(self):
        # Non-admins only see active types
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.role.name == 'admin':
            return ProcessType.objects.all()
        return ProcessType.objects.filter(is_active=True)


class ProcessViewSet(viewsets.ModelViewSet):
    """
    API endpoint for processes (expedientes).

    Provides CRUD with role-based filtering and nested steps.
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'file_number', 'title', 'description',
        'client__first_name', 'client__last_name',
        'external_reference'
    ]
    ordering_fields = ['created_at', 'due_date', 'priority', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        # Gestores and admins see all processes
        if hasattr(user, 'profile') and user.profile.role.name in ('admin', 'manager'):
            return Process.objects.select_related(
                'client', 'process_type', 'gestor', 'operator'
            ).prefetch_related('steps')
        # Others see processes they're involved in
        return Process.objects.select_related(
            'client', 'process_type', 'gestor', 'operator'
        ).prefetch_related('steps').filter(
            Q(gestor=user) | Q(operator=user) | Q(client__assigned_to=user)
        ).distinct()

    def get_serializer_class(self):
        if self.action == 'list':
            return ProcessListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return ProcessCreateUpdateSerializer
        return ProcessDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Group processes by status for dashboard."""
        status_counts = {}
        for status_choice in Process.STATUS_CHOICES:
            status_value = status_choice[0]
            count = self.get_queryset().filter(status=status_value).count()
            status_counts[status_value] = count
        return Response(status_counts)

    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """List documents for a specific process."""
        process = self.get_object()
        from apps.documents.serializers import DocumentSerializer
        documents = process.documents.all()
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        """Generate PDF summary for this process."""
        from django.http import HttpResponse
        from docgen.services.pdf_generator import generate_process_summary, WEASYPRINT_AVAILABLE

        if not WEASYPRINT_AVAILABLE:
            return Response(
                {'error': 'WeasyPrint no está instalado'},
                status=503
            )

        process = self.get_object()
        pdf_path = generate_process_summary(process)

        with open(pdf_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            filename = f"expediente_{process.file_number}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

    @action(detail=True, methods=['post'])
    def add_step(self, request, pk=None):
        """Add a step to a process."""
        process = self.get_object()
        serializer = ProcessStepSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(process=process)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
