"""
Agent Module Models
Contains agent-specific models if needed (currently using core models)
"""
from django.db import models

# Agent module uses models from core (User, AgentAssignment)
# and client_module (Order, SourcingRequest)
# This file is kept for future agent-specific features

class AgentNote(models.Model):
    """Internal notes for agents about clients or orders"""
    
    import uuid
    from django.utils import timezone
    from core.models import User
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agent_notes', limit_choices_to={'role': 'AGENT'})
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes_about_me', limit_choices_to={'role': 'CLIENT'}, null=True, blank=True)
    order = models.ForeignKey('client_module.Order', on_delete=models.CASCADE, related_name='agent_notes', null=True, blank=True)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'agent_notes'
        ordering = ['-created_at']
    
    def __str__(self):
        if self.client:
            return f"Note by {self.agent.full_name} about {self.client.full_name}"
        elif self.order:
            return f"Note by {self.agent.full_name} about {self.order.order_code}"
        return f"Note by {self.agent.full_name}"