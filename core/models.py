"""
Core models for SinoConnect Africa
Contains User, Currency, Notification, and other shared models
"""
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Custom User model with role-based access"""
    
    ROLE_CHOICES = [
        ('CLIENT', 'Client'),
        ('AGENT', 'Agent'),
        ('ADMIN', 'Administrateur'),
    ]
    
    ACCOUNT_TYPE_CHOICES = [
        ('STANDARD', 'Standard'),
        ('PRO', 'Professionnel'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CLIENT')
    account_type = models.CharField(
        max_length=10, 
        choices=ACCOUNT_TYPE_CHOICES, 
        default='STANDARD',
        blank=True,
        null=True
    )
    full_name = models.CharField(max_length=255)
    city = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"
    
    def get_unread_notifications_count(self):
        """Get count of unread notifications"""
        return self.notifications.filter(read=False).count()
    
    def is_client(self):
        return self.role == 'CLIENT'
    
    def is_agent(self):
        return self.role == 'AGENT'
    
    def is_admin(self):
        return self.role == 'ADMIN'


class Currency(models.Model):
    """Currency model for multi-currency support"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=3, unique=True)  # USD, XAF, EUR, etc.
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    exchange_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        help_text="Exchange rate to USD (1 USD = X in this currency)"
    )
    is_active = models.BooleanField(default=True)
    is_base = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'currencies'
        verbose_name_plural = 'Currencies'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one base currency
        if self.is_base:
            Currency.objects.filter(is_base=True).update(is_base=False)
            self.exchange_rate = 1.0000  # Base currency always has rate 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_base_currency(cls):
        """Get the base currency (USD by default)"""
        return cls.objects.filter(is_base=True).first()
    
    def convert_from_base(self, amount):
        """Convert amount from base currency to this currency"""
        return amount * self.exchange_rate
    
    def convert_to_base(self, amount):
        """Convert amount from this currency to base currency"""
        if self.exchange_rate > 0:
            return amount / self.exchange_rate
        return 0


class Notification(models.Model):
    """Notification model for in-app notifications"""
    
    TYPE_CHOICES = [
        ('COMMANDE', 'Commande'),
        ('SOURCING', 'Sourcing'),
        ('MESSAGE_AGENT', 'Message Agent'),
        ('PAYMENT', 'Paiement'),
        ('SYSTEM', 'Système'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True, null=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.read = True
        self.save()


class AgentAssignment(models.Model):
    """Agent assignment to clients"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='agent_assignment',
        limit_choices_to={'role': 'CLIENT'}
    )
    agent = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='assigned_clients',
        limit_choices_to={'role': 'AGENT'}
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'agent_assignments'
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.client.full_name} → {self.agent.full_name if self.agent else 'Non assigné'}"


class Category(models.Model):
    """Product category model"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, default='fas fa-box')  # FontAwesome icon class
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Product model"""
    
    STOCK_STATUS_CHOICES = [
        ('IN_STOCK', 'En Stock'),
        ('ON_ORDER', 'Sur Commande'),
        ('OUT_OF_STOCK', 'Rupture de Stock'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    price_usd = models.DecimalField(max_digits=10, decimal_places=2)  # Base price in USD
    stock_quantity = models.IntegerField(default=0)
    stock_status = models.CharField(max_length=20, choices=STOCK_STATUS_CHOICES, default='IN_STOCK')
    image = models.ImageField(upload_to='products/')
    additional_images = models.JSONField(default=list, blank=True)  # Store array of image URLs
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_price_in_currency(self, currency):
        """Get product price in specified currency"""
        if isinstance(currency, str):
            currency = Currency.objects.filter(code=currency, is_active=True).first()
        
        if currency and not currency.is_base:
            return self.price_usd * currency.exchange_rate
        return self.price_usd
    
    def is_in_stock(self):
        return self.stock_status == 'IN_STOCK' and self.stock_quantity > 0


class SiteSettings(models.Model):
    """Site-wide settings"""
    
    site_name = models.CharField(max_length=100, default='SinoConnect Africa')
    site_tagline = models.CharField(max_length=255, default='Importation Chine → Afrique')
    contact_email = models.EmailField(default='contact@sinoconnect.com')
    contact_phone = models.CharField(max_length=20, default='+1234567890')
    whatsapp_number = models.CharField(max_length=20, default='+1234567890')
    address = models.TextField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    
    class Meta:
        db_table = 'site_settings'
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return self.site_name
    
    @classmethod
    def get_settings(cls):
        """Get or create site settings"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings