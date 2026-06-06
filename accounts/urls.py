from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    RegisterTeamMemberView,
    TeamMemberListView,
    TeamMemberDetailView,
    UserProfileView,
    ChangePasswordView,
)

urlpatterns = [
    # JWT Authentication
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Admin - Team Member Management
    path('register/', RegisterTeamMemberView.as_view(), name='register_member'),
    path('team-members/', TeamMemberListView.as_view(), name='team_member_list'),
    path('team-members/<int:pk>/', TeamMemberDetailView.as_view(), name='team_member_detail'),

    # User Profile
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
]
