"""
Admin Module Django Admin Configuration
COMPLETE VERSION
"""
from django.contrib import admin
from .models import AdminNote, SystemSettings


@admin.register(AdminNote)
class AdminNoteAdmin(admin.ModelAdmin):
    """Admin Note admin interface"""
    list_display = ['admin', 'related_user', 'related_order', 'related_sourcing', 'created_at']
    list_filter = ['created_at', 'admin']
    search_fields = ['admin__full_name', 'related_user__full_name', 'note']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['admin', 'related_user', 'related_order', 'related_sourcing']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('admin', 'note')
        }),
        ('Relations', {
            'fields': ('related_user', 'related_order', 'related_sourcing')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    """System Settings admin interface"""
    list_display = ['maintenance_mode', 'new_user_registration_enabled', 'auto_agent_assignment_enabled', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Mode Maintenance', {
            'fields': ('maintenance_mode', 'maintenance_message')
        }),
        ('Paramètres Système', {
            'fields': ('new_user_registration_enabled', 'auto_agent_assignment_enabled')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one instance of system settings
        return not SystemSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of system settings
        return False