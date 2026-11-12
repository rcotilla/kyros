"""
Panel views — re-exports all view classes for backward compatibility.

Usage in urls.py:
    from .views import GestorHomeView, OperatorHomeView, ClientHomeView

For direct imports:
    from .views.gestor import GestorHomeView
    from .views.operator import OperatorHomeView
    from .views.client import ClientHomeView
    from .views.common import GestorRequiredMixin
"""

from .common import GestorRequiredMixin

from .gestor import (
    GestorHomeView,
    GestorClientListView, GestorClientCreateView,
    GestorClientDetailView, GestorClientEditView,
    GestorProcessListView, GestorProcessCreateView,
    GestorProcessDetailView, GestorProcessEditView,
    GestorProcessDeleteView,
    GestorProcessAddStepView, GestorProcessUpdateStepView,
    GestorProcessDeleteStepView, GestorProcessStepsUpdateView,
    GestorDocumentListView, GestorDocumentUploadView,
    GestorDocumentDeleteView, GestorDocumentGenerationView,
    GestorTemplateListView, GestorTemplateCreateView,
    GestorTemplateDetailView, GestorTemplateEditView,
    GestorTemplateAddStepView, GestorTemplateDeleteStepView,
)

from .operator import (
    OperatorHomeView,
    OperatorTaskDetailView,
    OperatorDocumentUploadView,
)

from .client import (
    ClientHomeView,
    ClientProcessDetailView,
    ClientProfileView,
)

__all__ = [
    # Common
    'GestorRequiredMixin',
    # Gestor — Dashboard
    'GestorHomeView',
    # Gestor — Clients
    'GestorClientListView', 'GestorClientCreateView',
    'GestorClientDetailView', 'GestorClientEditView',
    # Gestor — Processes
    'GestorProcessListView', 'GestorProcessCreateView',
    'GestorProcessDetailView', 'GestorProcessEditView',
    'GestorProcessDeleteView',
    'GestorProcessAddStepView', 'GestorProcessUpdateStepView',
    'GestorProcessDeleteStepView', 'GestorProcessStepsUpdateView',
    # Gestor — Documents
    'GestorDocumentListView', 'GestorDocumentUploadView',
    'GestorDocumentDeleteView', 'GestorDocumentGenerationView',
    # Gestor — Templates
    'GestorTemplateListView', 'GestorTemplateCreateView',
    'GestorTemplateDetailView', 'GestorTemplateEditView',
    'GestorTemplateAddStepView', 'GestorTemplateDeleteStepView',
    # Operator
    'OperatorHomeView',
    'OperatorTaskDetailView',
    'OperatorDocumentUploadView',
    # Client
    'ClientHomeView',
    'ClientProcessDetailView',
    'ClientProfileView',
]
