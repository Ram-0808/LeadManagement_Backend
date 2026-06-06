from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Lead, CallLog
from .serializers import (
    LeadSerializer,
    LeadDetailSerializer,
    CallLogSerializer,
    LogCallSerializer,
)


class IsAdmin(permissions.BasePermission):
    """Allow access only to admin/team lead users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsMember(permissions.BasePermission):
    """Allow access only to team member users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'member'


# ============================================
# TEAM MEMBER VIEWS
# ============================================

class LogCallView(generics.CreateAPIView):
    """
    Team member logs a new call.
    Creates the lead if it doesn't exist and records the call log.
    """
    serializer_class = LogCallSerializer
    permission_classes = [IsMember]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        call_log = serializer.save()
        response_serializer = CallLogSerializer(call_log)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class MyLeadsView(generics.ListAPIView):
    """
    Team member views all their assigned leads/contacts.
    """
    serializer_class = LeadSerializer
    permission_classes = [IsMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['interest_level', 'status']
    search_fields = ['client_name', 'phone', 'email']
    ordering_fields = ['created_at', 'interest_level', 'client_name']

    def get_queryset(self):
        return Lead.objects.filter(assigned_to=self.request.user)


class MyLeadDetailView(generics.RetrieveUpdateAPIView):
    """
    Team member views/updates a specific lead detail including call history.
    """
    serializer_class = LeadDetailSerializer
    permission_classes = [IsMember]

    def get_queryset(self):
        return Lead.objects.filter(assigned_to=self.request.user)


class MyCallLogsView(generics.ListAPIView):
    """
    Team member views their call history.
    """
    serializer_class = CallLogSerializer
    permission_classes = [IsMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['call_outcome', 'call_date']
    ordering_fields = ['call_date', 'call_time', 'call_duration']

    def get_queryset(self):
        return CallLog.objects.filter(called_by=self.request.user)


# ============================================
# ADMIN / TEAM LEAD VIEWS
# ============================================

class AdminAllLeadsView(generics.ListAPIView):
    """
    Admin/Team Lead views all leads from team members under them.
    """
    serializer_class = LeadSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['interest_level', 'status', 'assigned_to']
    search_fields = ['client_name', 'phone', 'email']
    ordering_fields = ['created_at', 'interest_level', 'assigned_to']

    def get_queryset(self):
        return Lead.objects.filter(assigned_to__team_lead=self.request.user)


class AdminLeadDetailView(generics.RetrieveAPIView):
    """
    Admin/Team Lead views specific lead details with call logs.
    """
    serializer_class = LeadDetailSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return Lead.objects.filter(assigned_to__team_lead=self.request.user)


class AdminMemberCallLogsView(generics.ListAPIView):
    """
    Admin/Team Lead views call logs of a specific team member.
    """
    serializer_class = CallLogSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['call_outcome', 'call_date']
    ordering_fields = ['call_date', 'call_time', 'call_duration']

    def get_queryset(self):
        member_id = self.kwargs.get('member_id')
        return CallLog.objects.filter(
            called_by_id=member_id,
            called_by__team_lead=self.request.user
        )
