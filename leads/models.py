from django.db import models
from django.conf import settings


class Lead(models.Model):
    """
    Represents a lead/client contact that a team member has reached out to.
    """
    INTEREST_CHOICES = (
        ('approved', 'Approved'),
        ('planning', 'Planning Soon'),
        ('followup', 'Need to Follow Up'),
        ('not_interested', 'Not Interested'),
    )

    STATUS_CHOICES = (
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('converted', 'Converted'),
        ('lost', 'Lost'),
    )

    # Lead/Client Details
    client_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Interest & Status
    interest_level = models.CharField(max_length=15, choices=INTEREST_CHOICES, default='followup')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')

    # Property Interest
    property_type = models.CharField(max_length=100, blank=True, null=True)
    budget_range = models.CharField(max_length=100, blank=True, null=True)
    preferred_location = models.CharField(max_length=200, blank=True, null=True)

    # Assignment
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leads'
    )

    # Notes
    notes = models.TextField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.client_name} - {self.phone} ({self.get_interest_level_display()})"


class CallLog(models.Model):
    """
    Logs every call made by a team member to a lead/client.
    """
    CALL_OUTCOME_CHOICES = (
        ('connected', 'Connected - Spoke to Client'),
        ('no_answer', 'No Answer'),
        ('busy', 'Busy'),
        ('callback', 'Requested Callback'),
        ('wrong_number', 'Wrong Number'),
        ('not_interested', 'Not Interested'),
    )

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='call_logs')
    called_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='call_logs'
    )

    # Call Details
    call_date = models.DateField(auto_now_add=True)
    call_time = models.TimeField(auto_now_add=True)
    call_duration = models.DurationField(help_text="Duration in HH:MM:SS format")
    call_outcome = models.CharField(max_length=15, choices=CALL_OUTCOME_CHOICES, default='connected')

    # Notes about the call
    notes = models.TextField(blank=True, null=True)
    follow_up_date = models.DateField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Call to {self.lead.client_name} by {self.called_by.full_name} on {self.call_date}"
