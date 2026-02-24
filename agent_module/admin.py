"""
Agent Module Admin Configuration
"""
from django.contrib import admin
from .models import AgentNote


@admin.register(AgentNote)
class AgentNoteAdmin(admin.ModelAdmin):
    """Agent Note admin"""
    list_display = ['agent', 'client', 'order', 'created_at']
    list_filter = ['created_at', 'agent']
    search_fields = ['agent__full_name', 'client__full_name', 'note']
    readonly_fields = ['created_at']
    raw_id_fields = ['agent', 'client', 'order']