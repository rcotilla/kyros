"""
PDF generation service using WeasyPrint.

Generates PDFs from HTML templates + context data.
Templates are stored in docgen/templates/docgen/pdf/ and can be
extended per process type (extranjería, marcas, etc.).
"""

import os
from pathlib import Path
from django.template.loader import render_to_string
from django.utils import timezone

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False


class PDFGenerator:
    """Generate PDF documents from HTML templates."""

    def __init__(self, template_name, context, output_filename=None):
        """
        Args:
            template_name: Path to HTML template (relative to docgen/templates/)
            context: Dict of data to pass to the template
            output_filename: Custom filename (without extension)
        """
        self.template_name = template_name
        self.context = context
        self.output_filename = output_filename

    def render_html(self):
        """Render the HTML template with context data."""
        return render_to_string(self.template_name, self.context)

    def generate(self, output_path=None):
        """
        Generate PDF file.

        Args:
            output_path: Full path for the output PDF file.
                        If None, generates in media/pdfs/

        Returns:
            Path to the generated PDF file.
        """
        if not WEASYPRINT_AVAILABLE:
            raise ImportError(
                "WeasyPrint no está instalado. "
                "Ejecutá: pip install weasyprint"
            )

        html_content = self.render_html()

        if output_path is None:
            from django.conf import settings
            pdf_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs')
            os.makedirs(pdf_dir, exist_ok=True)

            filename = self.output_filename or f"doc_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
            output_path = os.path.join(pdf_dir, f"{filename}.pdf")

        HTML(string=html_content).write_pdf(output_path)
        return output_path

    def generate_bytes(self):
        """Generate PDF and return as bytes (for direct response)."""
        if not WEASYPRINT_AVAILABLE:
            raise ImportError(
                "WeasyPrint no está instalado. "
                "Ejecutá: pip install weasyprint"
            )

        html_content = self.render_html()
        return HTML(string=html_content).write_pdf()


def generate_process_summary(process):
    """
    Generate a PDF summary for a process (expediente).

    Args:
        process: Process instance

    Returns:
        Path to the generated PDF file.
    """
    from apps.processes.models import Process

    context = {
        'process': process,
        'client': process.client,
        'process_type': process.process_type,
        'steps': process.steps.all().order_by('order'),
        'documents': process.documents.all(),
        'generated_at': timezone.now(),
        'gestor': process.gestor,
    }

    generator = PDFGenerator(
        template_name='pdf/process_summary.html',
        context=context,
        output_filename=f"expediente_{process.file_number}"
    )
    return generator.generate()


def generate_client_report(client):
    """
    Generate a PDF report for a client with all their processes.

    Args:
        client: Client instance

    Returns:
        Path to the generated PDF file.
    """
    from apps.clients.models import Client

    context = {
        'client': client,
        'processes': client.processes.all().order_by('-created_at'),
        'documents': client.documents.all(),
        'generated_at': timezone.now(),
    }

    generator = PDFGenerator(
        template_name='pdf/client_report.html',
        context=context,
        output_filename=f"cliente_{client.document_number}"
    )
    return generator.generate()
