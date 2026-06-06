from django.urls import path

from .views import (
    # Team Member Views
    LogCallView,
    MyLeadsView,
    MyLeadDetailView,
    MyCallLogsView,
    # Admin Views
    AdminAllLeadsView,
    AdminLeadDetailView,
    AdminMemberCallLogsView,
)

urlpatterns = [
    # Team Member URLs
    path('log-call/', LogCallView.as_view(), name='log_call'),
    path('my-leads/', MyLeadsView.as_view(), name='my_leads'),
    path('my-leads/<int:pk>/', MyLeadDetailView.as_view(), name='my_lead_detail'),
    path('my-calls/', MyCallLogsView.as_view(), name='my_call_logs'),

    # Admin / Team Lead URLs
    path('admin/all/', AdminAllLeadsView.as_view(), name='admin_all_leads'),
    path('admin/<int:pk>/', AdminLeadDetailView.as_view(), name='admin_lead_detail'),
    path('admin/member/<int:member_id>/calls/', AdminMemberCallLogsView.as_view(), name='admin_member_calls'),
]
