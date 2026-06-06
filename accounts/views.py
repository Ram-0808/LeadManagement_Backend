from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model

from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
)

User = get_user_model()


class IsAdmin(permissions.BasePermission):
    """Allow access only to admin/team lead users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class RegisterTeamMemberView(generics.CreateAPIView):
    """
    Admin/Team Lead registers a new team member.
    The new member is automatically assigned under the admin who creates them.
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [IsAdmin]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context


class TeamMemberListView(generics.ListAPIView):
    """
    Admin/Team Lead views all team members assigned to them.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return User.objects.filter(team_lead=self.request.user, role='member')


class TeamMemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Admin/Team Lead views, updates, or deactivates a specific team member.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return User.objects.filter(team_lead=self.request.user, role='member')

    def perform_destroy(self, instance):
        # Soft delete - deactivate instead of hard delete
        instance.is_active = False
        instance.save()


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Authenticated user views/updates their own profile.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """
    Authenticated user changes their own password.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
