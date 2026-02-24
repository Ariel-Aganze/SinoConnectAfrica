"""
Admin Module Models
"""
import uuid
from django.db import models
from core.models import User


class AdminNote(models.Model):
    """Admin notes for internal tracking"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_notes', limit_choices_to={'role': 'ADMIN'})
    related_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes_about', null=True, blank=True)
    related_order = models.ForeignKey('client_module.Order', on_delete=models.CASCADE, null=True, blank=True)
    related_sourcing = models.ForeignKey('client_module.SourcingRequest', on_delete=models.CASCADE, null=True, blank=True)
    
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'admin_notes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note by {self.admin.full_name} - {self.created_at.strftime('%Y-%m-%d')}"


class SystemSettings(models.Model):
    """System-wide settings"""
    
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True, null=True)
    new_user_registration_enabled = models.BooleanField(default=True)
    auto_agent_assignment_enabled = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_settings'
        verbose_name = 'System Settings'
        verbose_name_plural = 'System Settings'
    
    def __str__(self):
        return "System Settings"
    
    @classmethod
    def get_settings(cls):
        """Get or create system settings"""
        settings, created = cls.objects.get_or_create(id=1)
        return settings