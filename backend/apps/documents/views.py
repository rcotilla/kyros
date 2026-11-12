"""Views for documents app."""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    """API endpoint for documents."""
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        """Return only documents owned by the current user."""
        return Document.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """Automatically set the owner to the current user."""
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def my_documents(self, request):
        """List all documents of the current user."""
        documents = self.get_queryset()
        serializer = self.get_serializer(documents, many=True)
        return Response(serializer.data)
