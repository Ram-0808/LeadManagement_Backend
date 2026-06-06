"""
URL configuration for leadmanagement project.
Royal Reality Groups - Lead Management System
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/leads/', include('leads.urls')),
    path('api/reports/', include('reports.urls')),
]
