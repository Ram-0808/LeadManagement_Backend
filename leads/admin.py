from django.contrib import admin
from .models import Lead, CallLog


class CallLogInline(admin.TabularInline):
    model = CallLog
    extra = 0
    readonly_fields = ['call_date', 'call_time', 'created_at']


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'phone', 'interest_level', 'status', 'assigned_to', 'created_at']
    list_filter = ['interest_level', 'status', 'assigned_to', 'created_at']
    search_fields = ['client_name', 'phone', 'email']
    inlines = [CallLogInline]


@admin.register(CallLog)
class CallLogAdmin(admin.ModelAdmin):
    list_display = ['lead', 'called_by', 'call_date', 'call_duration', 'call_outcome']
    list_filter = ['call_outcome', 'call_date', 'called_by']
    search_fields = ['lead__client_name', 'notes']
    readonly_fields = ['call_date', 'call_time', 'created_at']
