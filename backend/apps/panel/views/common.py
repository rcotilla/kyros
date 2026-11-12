"""Common mixins and utilities for panel views."""

from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


class GestorRequiredMixin:
    """Mixin that restricts access to gestor and admin roles."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('landing:home')

        if hasattr(request.user, 'profile'):
            role = request.user.profile.role.name
            if role in ('admin', 'manager'):
                return super().dispatch(request, *args, **kwargs)

        messages.error(request, _('No tenés acceso a esta sección.'))
        return redirect('landing:home')
