from rest_framework import serializers
from .models import Lead, CallLog


class CallLogSerializer(serializers.ModelSerializer):
    """Serializer for call logs."""
    called_by_name = serializers.SerializerMethodField()
    lead_name = serializers.SerializerMethodField()

    class Meta:
        model = CallLog
        fields = [
            'id', 'lead', 'lead_name', 'called_by', 'called_by_name',
            'call_date', 'call_time', 'call_duration', 'call_outcome',
            'notes', 'follow_up_date', 'created_at'
        ]
        read_only_fields = ['id', 'called_by', 'call_date', 'call_time', 'created_at']

    def get_called_by_name(self, obj):
        return obj.called_by.full_name

    def get_lead_name(self, obj):
        return obj.lead.client_name


class LeadSerializer(serializers.ModelSerializer):
    """Serializer for lead/client details."""
    assigned_to_name = serializers.SerializerMethodField()
    total_calls = serializers.SerializerMethodField()
    last_call_date = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = [
            'id', 'client_name', 'phone', 'email', 'address',
            'interest_level', 'status', 'property_type', 'budget_range',
            'preferred_location', 'assigned_to', 'assigned_to_name',
            'notes', 'total_calls', 'last_call_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'assigned_to', 'created_at', 'updated_at']

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.full_name

    def get_total_calls(self, obj):
        return obj.call_logs.count()

    def get_last_call_date(self, obj):
        last_call = obj.call_logs.first()
        return last_call.call_date if last_call else None


class LeadDetailSerializer(LeadSerializer):
    """Detailed lead serializer including call history."""
    call_logs = CallLogSerializer(many=True, read_only=True)

    class Meta(LeadSerializer.Meta):
        fields = LeadSerializer.Meta.fields + ['call_logs']


class LogCallSerializer(serializers.ModelSerializer):
    """
    Serializer for team members to log a new call.
    Creates both the lead (if new) and the call log entry.
    """
    client_name = serializers.CharField(max_length=200)
    phone = serializers.CharField(max_length=15)
    interest_level = serializers.ChoiceField(choices=Lead.INTEREST_CHOICES)
    call_duration = serializers.DurationField()
    call_outcome = serializers.ChoiceField(choices=CallLog.CALL_OUTCOME_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)
    follow_up_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = CallLog
        fields = [
            'client_name', 'phone', 'interest_level',
            'call_duration', 'call_outcome', 'notes', 'follow_up_date'
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        client_name = validated_data.pop('client_name')
        phone = validated_data.pop('phone')
        interest_level = validated_data.pop('interest_level')

        # Get or create lead
        lead, created = Lead.objects.get_or_create(
            phone=phone,
            assigned_to=user,
            defaults={
                'client_name': client_name,
                'interest_level': interest_level,
                'status': 'contacted',
            }
        )

        # Update lead interest if not new
        if not created:
            lead.interest_level = interest_level
            lead.client_name = client_name
            lead.save()

        # Create call log
        call_log = CallLog.objects.create(
            lead=lead,
            called_by=user,
            **validated_data
        )

        return call_log
