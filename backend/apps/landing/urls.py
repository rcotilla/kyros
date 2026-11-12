"""URL configuration for landing app."""

from django.urls import path
from .views import (
    LandingView, ContactView, LoginView, LogoutView, DashboardView
)

app_name = 'landing'

urlpatterns = [
    path('', LandingView.as_view(), name='home'),
    path('contacto/', ContactView.as_view(), name='contact'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
