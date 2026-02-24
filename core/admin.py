"""
Django admin configuration for core models
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Currency, Notification, AgentAssignment, 
    Category, Product, SiteSettings
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin"""
    list_display = ['email', 'full_name', 'role', 'account_type', 'city', 'is_active', 'created_at']
    list_filter = ['role', 'account_type', 'is_active', 'city']
    search_fields = ['email', 'full_name', 'phone_number']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('full_name', 'phone_number', 'city', 'avatar')}),
        ('Permissions', {'fields': ('role', 'account_type', 'is_active', 'is_staff', 'is_superuser')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    """Currency admin"""
    list_display = ['code', 'name', 'symbol', 'exchange_rate', 'is_base', 'is_active']
    list_filter = ['is_active', 'is_base']
    search_fields = ['code', 'name']
    ordering = ['code']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Notification admin"""
    list_display = ['user', 'type', 'title', 'read', 'created_at']
    list_filter = ['type', 'read', 'created_at']
    search_fields = ['user__email', 'user__full_name', 'title', 'message']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(AgentAssignment)
class AgentAssignmentAdmin(admin.ModelAdmin):
    """Agent Assignment admin"""
    list_display = ['client', 'agent', 'assigned_at']
    list_filter = ['assigned_at']
    search_fields = ['client__full_name', 'agent__full_name']
    ordering = ['-assigned_at']
    raw_id_fields = ['client', 'agent']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category admin"""
    list_display = ['name', 'slug', 'icon', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Product admin"""
    list_display = ['name', 'category', 'price_usd', 'stock_quantity', 'stock_status', 'is_active', 'featured']
    list_filter = ['stock_status', 'is_active', 'featured', 'category']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['-created_at']
    list_editable = ['stock_status', 'is_active', 'featured']


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Site Settings admin"""
    list_display = ['site_name', 'contact_email', 'contact_phone']
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion
        return False