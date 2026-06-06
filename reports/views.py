from datetime import date, timedelta
from io import BytesIO

from django.http import HttpResponse
from django.db.models import Count, Sum, Q
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from leads.models import Lead, CallLog
from .serializers import TeamMemberPerformanceSerializer, DashboardSummarySerializer

import openpyxl


class IsAdmin(permissions.BasePermission):
    """Allow access only to admin/team lead users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class DashboardView(APIView):
    """
    Admin/Team Lead dashboard with aggregate performance metrics.
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        user = request.user
        team_members = User.objects.filter(team_lead=user, role='member', is_active=True)
        team_member_ids = team_members.values_list('id', flat=True)

        today = date.today()

        total_leads = Lead.objects.filter(assigned_to__in=team_member_ids).count()
        total_calls = CallLog.objects.filter(called_by__in=team_member_ids).count()
        leads_today = Lead.objects.filter(
            assigned_to__in=team_member_ids, created_at__date=today
        ).count()
        calls_today = CallLog.objects.filter(
            called_by__in=team_member_ids, call_date=today
        ).count()
        hot_leads = Lead.objects.filter(
            assigned_to__in=team_member_ids, interest_level='approved'
        ).count()
        converted_leads = Lead.objects.filter(
            assigned_to__in=team_member_ids, status='converted'
        ).count()

        # Top performers (by total calls this week)
        week_start = today - timedelta(days=today.weekday())
        top_performers = []
        for member in team_members[:5]:
            member_leads = Lead.objects.filter(assigned_to=member)
            member_calls = CallLog.objects.filter(called_by=member)
            top_performers.append({
                'member_id': member.id,
                'member_name': member.full_name,
                'total_leads': member_leads.count(),
                'total_calls': member_calls.count(),
                'hot_leads': member_leads.filter(interest_level='approved').count(),
                'warm_leads': member_leads.filter(interest_level='planning').count(),
                'cold_leads': member_leads.filter(interest_level='not_interested').count(),
                'converted_leads': member_leads.filter(status='converted').count(),
                'total_call_duration': member_calls.aggregate(
                    total=Sum('call_duration')
                )['total'] or timedelta(0),
                'calls_today': member_calls.filter(call_date=today).count(),
                'leads_today': member_leads.filter(created_at__date=today).count(),
            })

        data = {
            'total_team_members': team_members.count(),
            'total_leads': total_leads,
            'total_calls': total_calls,
            'leads_today': leads_today,
            'calls_today': calls_today,
            'hot_leads': hot_leads,
            'converted_leads': converted_leads,
            'top_performers': top_performers,
        }

        serializer = DashboardSummarySerializer(data)
        return Response(serializer.data)


class TeamMemberPerformanceView(APIView):
    """
    Admin views detailed performance report for all team members.
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        user = request.user
        team_members = User.objects.filter(team_lead=user, role='member', is_active=True)
        today = date.today()

        performance_data = []
        for member in team_members:
            member_leads = Lead.objects.filter(assigned_to=member)
            member_calls = CallLog.objects.filter(called_by=member)
            performance_data.append({
                'member_id': member.id,
                'member_name': member.full_name,
                'total_leads': member_leads.count(),
                'total_calls': member_calls.count(),
                'hot_leads': member_leads.filter(interest_level='approved').count(),
                'warm_leads': member_leads.filter(interest_level='planning').count(),
                'cold_leads': member_leads.filter(interest_level='not_interested').count(),
                'converted_leads': member_leads.filter(status='converted').count(),
                'total_call_duration': member_calls.aggregate(
                    total=Sum('call_duration')
                )['total'] or timedelta(0),
                'calls_today': member_calls.filter(call_date=today).count(),
                'leads_today': member_leads.filter(created_at__date=today).count(),
            })

        serializer = TeamMemberPerformanceSerializer(performance_data, many=True)
        return Response(serializer.data)


class ExportLeadsExcelView(APIView):
    """
    Admin exports all leads data as an Excel file.
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        user = request.user
        leads = Lead.objects.filter(assigned_to__team_lead=user).select_related('assigned_to')

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = 'Leads Report'

        # Header row
        headers = [
            'Client Name', 'Phone', 'Email', 'Interest Level', 'Status',
            'Property Type', 'Budget Range', 'Preferred Location',
            'Assigned To', 'Notes', 'Created Date'
        ]
        sheet.append(headers)

        # Data rows
        for lead in leads:
            sheet.append([
                lead.client_name,
                lead.phone,
                lead.email or '',
                lead.get_interest_level_display(),
                lead.get_status_display(),
                lead.property_type or '',
                lead.budget_range or '',
                lead.preferred_location or '',
                lead.assigned_to.full_name,
                lead.notes or '',
                lead.created_at.strftime('%Y-%m-%d %H:%M'),
            ])

        # Prepare response
        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="leads_report_{date.today()}.xlsx"'
        return response


class ExportMemberLeadsExcelView(APIView):
    """
    Admin exports leads data for a specific team member as an Excel file.
    """
    permission_classes = [IsAdmin]

    def get(self, request, member_id):
        user = request.user
        # Ensure the member belongs to this admin
        try:
            member = User.objects.get(id=member_id, team_lead=user, role='member')
        except User.DoesNotExist:
            return Response({'detail': 'Member not found'}, status=404)

        leads = Lead.objects.filter(assigned_to=member)
        call_logs = CallLog.objects.filter(called_by=member).select_related('lead')

        workbook = openpyxl.Workbook()

        # Sheet 1: Leads
        leads_sheet = workbook.active
        leads_sheet.title = 'Leads'
        leads_sheet.append([
            'Client Name', 'Phone', 'Email', 'Interest Level', 'Status',
            'Property Type', 'Budget Range', 'Preferred Location',
            'Notes', 'Created Date'
        ])
        for lead in leads:
            leads_sheet.append([
                lead.client_name,
                lead.phone,
                lead.email or '',
                lead.get_interest_level_display(),
                lead.get_status_display(),
                lead.property_type or '',
                lead.budget_range or '',
                lead.preferred_location or '',
                lead.notes or '',
                lead.created_at.strftime('%Y-%m-%d %H:%M'),
            ])

        # Sheet 2: Call Logs
        calls_sheet = workbook.create_sheet('Call Logs')
        calls_sheet.append([
            'Date', 'Time', 'Client Name', 'Phone', 'Duration',
            'Outcome', 'Notes', 'Follow Up Date'
        ])
        for log in call_logs:
            calls_sheet.append([
                str(log.call_date),
                str(log.call_time),
                log.lead.client_name,
                log.lead.phone,
                str(log.call_duration),
                log.get_call_outcome_display(),
                log.notes or '',
                str(log.follow_up_date) if log.follow_up_date else '',
            ])

        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        safe_name = member.full_name.replace(' ', '_')
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{safe_name}_leads_{date.today()}.xlsx"'
        return response


class ExportTeamMembersExcelView(APIView):
    """
    Admin exports all team member details with performance stats as an Excel file.
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        user = request.user
        team_members = User.objects.filter(team_lead=user, role='member')
        today = date.today()

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = 'Team Members Report'

        # Header row
        headers = [
            'Name', 'Username', 'Email', 'Phone', 'Status',
            'Date Joined', 'Total Leads', 'Total Calls',
            'Approved', 'Planning Soon', 'Not Interested', 'Converted',
            'Calls Today'
        ]
        sheet.append(headers)

        # Data rows
        for member in team_members:
            member_leads = Lead.objects.filter(assigned_to=member)
            member_calls = CallLog.objects.filter(called_by=member)
            sheet.append([
                member.full_name,
                member.username,
                member.email or '',
                member.phone or '',
                'Active' if member.is_active else 'Inactive',
                member.date_joined.strftime('%Y-%m-%d'),
                member_leads.count(),
                member_calls.count(),
                member_leads.filter(interest_level='approved').count(),
                member_leads.filter(interest_level='planning').count(),
                member_leads.filter(interest_level='not_interested').count(),
                member_leads.filter(status='converted').count(),
                member_calls.filter(call_date=today).count(),
            ])

        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="team_members_report_{date.today()}.xlsx"'
        return response


class ExportCallLogsExcelView(APIView):
    """
    Admin exports all call logs data as an Excel file.
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        user = request.user
        call_logs = CallLog.objects.filter(
            called_by__team_lead=user
        ).select_related('lead', 'called_by')

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = 'Call Logs Report'

        # Header row
        headers = [
            'Date', 'Time', 'Team Member', 'Client Name', 'Phone',
            'Call Duration', 'Call Outcome', 'Notes', 'Follow Up Date'
        ]
        sheet.append(headers)

        # Data rows
        for log in call_logs:
            sheet.append([
                str(log.call_date),
                str(log.call_time),
                log.called_by.full_name,
                log.lead.client_name,
                log.lead.phone,
                str(log.call_duration),
                log.get_call_outcome_display(),
                log.notes or '',
                str(log.follow_up_date) if log.follow_up_date else '',
            ])

        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="call_logs_report_{date.today()}.xlsx"'
        return response
