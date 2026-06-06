from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'team_lead', 'is_active']
    list_filter = ['role', 'is_active', 'team_lead']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Team', {'fields': ('role', 'phone', 'team_lead')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role & Team', {'fields': ('role', 'phone', 'team_lead')}),
    )
