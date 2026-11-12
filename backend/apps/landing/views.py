"""Views for landing app."""

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from .models import ContactMessage


class LandingView(View):
    """Landing page view."""

    def get(self, request):
        context = {
            'title': 'KAIROS - Plataforma de Gestión de Procesos',
            'description': 'Solución integral para la gestión de procesos de gestoría.',
        }
        return render(request, 'landing/index.html', context)


class ContactView(View):
    """Handle contact form submissions from the landing page."""

    def post(self, request):
        name = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('mensaje', '').strip()

        if not all([name, email, message]):
            messages.error(request, _('Por favor completá todos los campos.'))
            return self._redirect_home_with_contact_fragment()

        ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            ip_address = ip_address.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message,
            ip_address=ip_address,
        )

        messages.success(
            request,
            _('¡Mensaje enviado correctamente! Te contactaremos pronto.')
        )
        return self._redirect_home_with_contact_fragment()

    def _redirect_home_with_contact_fragment(self):
        """Redirect to the landing home page with the #contacto fragment."""
        return HttpResponseRedirect(f"{reverse('landing:home')}#contacto")


class LoginView(View):
    """Handle user login via session (not JWT)."""

    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, _('Por favor ingresá usuario y contraseña.'))
            return redirect('landing:home')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, _('¡Bienvenido, %(name)s!') % {
                    'name': user.get_full_name() or user.username
                })
                # Redirect to panel based on role
                if hasattr(user, 'profile'):
                    role = user.profile.role.name
                    if role in ('admin', 'manager'):
                        return redirect('panel:home')
                    elif role == 'operator':
                        return redirect('panel:operator_home')
                    elif role == 'client':
                        return redirect('panel:client_home')
                # Fallback
                return redirect('panel:home')
            else:
                messages.error(request, _('Tu cuenta está desactivada. Contactá al administrador.'))
        else:
            messages.error(request, _('Usuario o contraseña incorrectos.'))

        return redirect('landing:home')


class LogoutView(View):
    """Handle user logout."""

    def get(self, request):
        logout(request)
        messages.info(request, _('Cerraste sesión correctamente.'))
        return redirect('landing:home')


class DashboardView(View):
    """Dashboard that shows content based on user role."""

    @method_decorator(login_required(login_url='/'))
    def get(self, request):
        user = request.user
        role = None

        if hasattr(user, 'profile'):
            role = user.profile.role.name

        context = {
            'user': user,
            'role': role,
        }

        # Route based on role
        if role == 'admin':
            return render(request, 'dashboard/admin.html', context)
        elif role == 'manager':
            return render(request, 'dashboard/manager.html', context)
        elif role == 'operator':
            return render(request, 'dashboard/operator.html', context)
        elif role == 'client':
            return render(request, 'dashboard/client.html', context)
        else:
            # No profile or unknown role
            return render(request, 'dashboard/default.html', context)
