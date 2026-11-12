"""
Documents models — re-exports for backward compatibility.

Usage:
    from apps.documents.models import Document

For direct imports:
    from apps.documents.models.uploaded import Document
"""

from .uploaded import Document

__all__ = [
    'Document',
]
