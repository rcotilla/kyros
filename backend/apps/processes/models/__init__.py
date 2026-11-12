"""
Process models — re-exports for backward compatibility.

Usage:
    from apps.processes.models import Process, ProcessType, ProcessStep

For direct imports:
    from apps.processes.models.types import ProcessType
    from apps.processes.models.process import Process
    from apps.processes.models.step import ProcessStep
    from apps.processes.models.template import ProcessTemplate, ProcessTemplateStep
"""

from .types import ProcessType
from .process import Process
from .step import ProcessStep
from .template import ProcessTemplate, ProcessTemplateStep

__all__ = [
    'ProcessType',
    'Process',
    'ProcessStep',
    'ProcessTemplate',
    'ProcessTemplateStep',
]
