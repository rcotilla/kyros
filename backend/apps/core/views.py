"""
Views for core app.

Provides REST API endpoints for:
- Authentication (via JWT tokens)
- User profile retrieval and updates
- Role information
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User

from .models import UserProfile, Role
from .serializers import (
    UserProfileSerializer,
    UserDetailSerializer,
    UserCreateSerializer,
    ChangePasswordSerializer,
    RoleSerializer
)


class UserProfileViewSet(viewsets.ViewSet):
    """
    API endpoint for user profiles.

    Provides:
    - /api/user/profile/ - Get current user's profile
    - /api/user/profile/update/ - Update current user's profile
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get current user's profile."""
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Perfil de usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user's profile."""
        try:
            profile = UserProfile.objects.get(user=request.user)

            # Allow updating only certain fields
            if 'company' in request.data:
                profile.company = request.data['company']
            if 'phone' in request.data:
                profile.phone = request.data['phone']

            profile.save()
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Perfil de usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change current user's password."""
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user

            # Verify old password.
            # NOTE: old_password/new_password are write_only, so they are only
            # available through serializer.validated_data, not serializer.data.
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'old_password': 'La contraseña actual es incorrecta'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({'detail': 'Contraseña actualizada correctamente'})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for roles (read-only).

    Lists available roles in the system:
    - client: Cliente
    - manager: Gestor
    - operator: Operador
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_role(self, request):
        """Get current user's role information."""
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = RoleSerializer(profile.role)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Rol de usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )


class AuthStatusView(viewsets.ViewSet):
    """
    API endpoint for authentication status.

    Used by Flet frontend to verify token and get user info.
    """

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def status(self, request):
        """Get current authentication status and user info."""
        try:
            profile = UserProfile.objects.get(user=request.user)
            profile_data = UserProfileSerializer(profile).data

            return Response({
                'authenticated': True,
                'user': UserDetailSerializer(request.user).data,
                'profile': profile_data
            })
        except UserProfile.DoesNotExist:
            return Response({
                'authenticated': True,
                'user': UserDetailSerializer(request.user).data,
                'profile': None
            })

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Register a new user (for Fase 1 public registration)."""
        serializer = UserCreateSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # Create UserProfile with default role (client)
            client_role, _ = Role.objects.get_or_create(
                name='client',
                defaults={'description': 'Cliente por defecto'}
            )
            UserProfile.objects.create(user=user, role=client_role)

            return Response(
                UserDetailSerializer(user).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
