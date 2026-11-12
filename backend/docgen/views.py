"""
Views for the docgen app.

Provides API endpoints for listing available document templates
and generating PDF documents on demand.
"""

import os

from django.conf import settings
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status

from .services.pdf_generator import PDFGenerator, WEASYPRINT_AVAILABLE


class TemplateListView(APIView):
    """List available document templates."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        templates_dir = os.path.join(
            settings.BASE_DIR, 'docgen', 'templates', 'docgen', 'pdf'
        )
        templates = []
        if os.path.isdir(templates_dir):
            for filename in sorted(os.listdir(templates_dir)):
                if filename.endswith('.html') and filename != 'base.html':
                    templates.append({
                        'name': filename.replace('.html', ''),
                        'path': f'docgen/pdf/{filename}',
                    })
        return Response({'templates': templates})


class GenerateDocumentView(APIView):
    """Generate a PDF document from a template + data."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not WEASYPRINT_AVAILABLE:
            return Response(
                {'error': 'WeasyPrint no está instalado.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        template_name = request.data.get('template_name')
        data = request.data.get('data', {})

        if not template_name:
            return Response(
                {'error': 'template_name es requerido.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Map short template name to full template path
        template_path = f'docgen/pdf/{template_name}.html'

        try:
            generator = PDFGenerator(
                template_name=template_path,
                context=data,
                output_filename=template_name,
            )
            pdf_bytes = generator.generate_bytes()
        except Exception as e:
            return Response(
                {'error': f'Error generando el documento: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        from django.http import HttpResponse
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="{template_name}.pdf"'
        )
        return response
