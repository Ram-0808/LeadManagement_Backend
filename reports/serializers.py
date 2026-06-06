from rest_framework import serializers


class TeamMemberPerformanceSerializer(serializers.Serializer):
    """Serializer for team member performance summary."""
    member_id = serializers.IntegerField()
    member_name = serializers.CharField()
    total_leads = serializers.IntegerField()
    total_calls = serializers.IntegerField()
    hot_leads = serializers.IntegerField()
    warm_leads = serializers.IntegerField()
    cold_leads = serializers.IntegerField()
    converted_leads = serializers.IntegerField()
    total_call_duration = serializers.DurationField()
    calls_today = serializers.IntegerField()
    leads_today = serializers.IntegerField()


class DashboardSummarySerializer(serializers.Serializer):
    """Serializer for admin dashboard summary."""
    total_team_members = serializers.IntegerField()
    total_leads = serializers.IntegerField()
    total_calls = serializers.IntegerField()
    leads_today = serializers.IntegerField()
    calls_today = serializers.IntegerField()
    hot_leads = serializers.IntegerField()
    converted_leads = serializers.IntegerField()
    top_performers = TeamMemberPerformanceSerializer(many=True)
