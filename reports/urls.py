from django.urls import path

from .views import (
    DashboardView,
    TeamMemberPerformanceView,
    ExportLeadsExcelView,
    ExportMemberLeadsExcelView,
    ExportTeamMembersExcelView,
    ExportCallLogsExcelView,
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('performance/', TeamMemberPerformanceView.as_view(), name='team_performance'),
    path('export/leads/', ExportLeadsExcelView.as_view(), name='export_leads_excel'),
    path('export/member/<int:member_id>/leads/', ExportMemberLeadsExcelView.as_view(), name='export_member_leads_excel'),
    path('export/team-members/', ExportTeamMembersExcelView.as_view(), name='export_team_members_excel'),
    path('export/call-logs/', ExportCallLogsExcelView.as_view(), name='export_call_logs_excel'),
]
