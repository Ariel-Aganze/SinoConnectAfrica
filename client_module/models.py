"""
Client Module Models
Contains Cart, CartItem, Order, OrderItem, SourcingRequest, Quote, Payment
"""
import uuid
from django.db import models
from django.utils import timezone
from core.models import User, Product, Currency


class Cart(models.Model):
    """Shopping cart model"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carts'
    
    def __str__(self):
        return f"Panier de {self.user.full_name}"
    
    def get_total_items(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    def get_total_price(self, currency=None):
        """Get total price in specified currency"""
        if not currency:
            currency = Currency.get_base_currency()
        
        total = sum(item.get_subtotal(currency) for item in self.items.all())
        return total
    
    def clear(self):
        """Clear all items from cart"""
        self.items.all().delete()


class CartItem(models.Model):
    """Cart item model"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cart_items'
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    
    def get_subtotal(self, currency=None):
        """Get subtotal price in specified currency"""
        price = self.product.get_price_in_currency(currency)
        return price * self.quantity


class Order(models.Model):
    """Order model"""
    
    STATUS_CHOICES = [
        ('EN_ATTENTE', 'En attente de paiement'),
        ('PAYE', 'Payé'),
        ('PREPARATION', 'En préparation'),
        ('EXPEDIE', 'Expédié'),
        ('EN_TRANSIT', 'En transit'),
        ('LIVRE', 'Livré'),
        ('PROBLEME', 'Problème'),
        ('ANNULE', 'Annulé'),
        ('RETOURNE', 'Retourné'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_code = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='EN_ATTENTE')
    
    # Pricing
    total_amount_usd = models.DecimalField(max_digits=10, decimal_places=2)
    currency_code = models.CharField(max_length=3, default='USD')
    total_amount_local = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Delivery information
    delivery_address = models.TextField()
    delivery_city = models.CharField(max_length=100)
    delivery_phone = models.CharField(max_length=20)
    
    # Notes
    customer_notes = models.TextField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    shipped_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order_code} - {self.user.full_name}"
    
    def save(self, *args, **kwargs):
        if not self.order_code:
            # Generate order code: CMD-YYYY-XXXX
            from django.db.models import Max
            last_order = Order.objects.filter(
                order_code__startswith=f'CMD-{timezone.now().year}'
            ).aggregate(Max('order_code'))
            
            if last_order['order_code__max']:
                last_number = int(last_order['order_code__max'].split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.order_code = f'CMD-{timezone.now().year}-{new_number:04d}'
        
        super().save(*args, **kwargs)
    
    def get_total_items(self):
        """Get total number of items"""
        return sum(item.quantity for item in self.items.all())
    
    def mark_as_paid(self):
        """Mark order as paid"""
        self.status = 'PAYE'
        self.paid_at = timezone.now()
        self.save()
    
    def mark_as_shipped(self):
        """Mark order as shipped"""
        self.status = 'EXPEDIE'
        self.shipped_at = timezone.now()
        self.save()
    
    def mark_as_delivered(self):
        """Mark order as delivered"""
        self.status = 'LIVRE'
        self.delivered_at = timezone.now()
        self.save()


class OrderItem(models.Model):
    """Order item model"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255)  # Snapshot of product name
    quantity = models.PositiveIntegerField()
    unit_price_usd = models.DecimalField(max_digits=10, decimal_places=2)  # Price at order time
    
    class Meta:
        db_table = 'order_items'
    
    def __str__(self):
        return f"{self.product_name} x{self.quantity}"
    
    def get_subtotal(self):
        """Get subtotal in USD"""
        return self.unit_price_usd * self.quantity


class SourcingRequest(models.Model):
    """Sourcing request model"""
    
    STATUS_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('EN_COURS', 'En cours de recherche'),
        ('DEVIS_ENVOYE', 'Devis envoyé'),
        ('VALIDE', 'Validé'),
        ('REJETE', 'Rejeté'),
        ('ANNULE', 'Annulé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_code = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sourcing_requests')
    
    # Product details
    product_name = models.CharField(max_length=255)
    product_description = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField()
    budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='sourcing/', blank=True, null=True)
    reference_url = models.URLField(blank=True, null=True, help_text="Lien Alibaba, Taobao, etc.")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='EN_ATTENTE')
    
    # Admin response
    admin_notes = models.TextField(blank=True, null=True)
    estimated_delivery_days = models.PositiveIntegerField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sourcing_requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.request_code} - {self.product_name}"
    
    def save(self, *args, **kwargs):
        if not self.request_code:
            # Generate request code: SR-YYYY-XXXX
            from django.db.models import Max
            last_request = SourcingRequest.objects.filter(
                request_code__startswith=f'SR-{timezone.now().year}'
            ).aggregate(Max('request_code'))
            
            if last_request['request_code__max']:
                last_number = int(last_request['request_code__max'].split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.request_code = f'SR-{timezone.now().year}-{new_number:04d}'
        
        super().save(*args, **kwargs)


class Quote(models.Model):
    """Quote model for sourcing requests"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sourcing_request = models.ForeignKey(SourcingRequest, on_delete=models.CASCADE, related_name='quotes')
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'ADMIN'})
    
    # Quote details
    quote_amount_usd = models.DecimalField(max_digits=10, decimal_places=2)
    currency_code = models.CharField(max_length=3, default='USD')
    quote_amount_local = models.DecimalField(max_digits=10, decimal_places=2)
    
    description = models.TextField()
    delivery_time_days = models.PositiveIntegerField(help_text="Délai de livraison en jours")
    valid_until = models.DateField(help_text="Date d'expiration du devis")
    
    # Files
    quote_document = models.FileField(upload_to='quotes/', blank=True, null=True)
    
    # Status
    accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quotes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Devis pour {self.sourcing_request.request_code}"
    
    def accept(self):
        """Accept the quote"""
        self.accepted = True
        self.accepted_at = timezone.now()
        self.save()
        
        # Update sourcing request status
        self.sourcing_request.status = 'VALIDE'
        self.sourcing_request.save()


class Payment(models.Model):
    """Payment model"""
    
    METHOD_CHOICES = [
        ('WHATSAPP', 'WhatsApp'),
        ('VIREMENT', 'Virement Bancaire'),
        ('CASH', 'Espèces'),
        ('MOBILE_MONEY', 'Mobile Money'),
    ]
    
    STATUS_CHOICES = [
        ('EN_ATTENTE', 'En attente de vérification'),
        ('CONFIRME', 'Confirmé'),
        ('REJETE', 'Rejeté'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='EN_ATTENTE')
    
    # Proof of payment
    proof_image = models.ImageField(upload_to='payments/', blank=True, null=True)
    transaction_reference = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Admin verification
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='verified_payments',
        limit_choices_to={'role': 'ADMIN'}
    )
    verified_at = models.DateTimeField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Paiement {self.order.order_code} - {self.amount} {self.order.currency_code}"
    
    def confirm(self, admin_user):
        """Confirm payment"""
        self.status = 'CONFIRME'
        self.verified_by = admin_user
        self.verified_at = timezone.now()
        self.save()
        
        # Mark order as paid
        self.order.mark_as_paid()
    
    def reject(self, admin_user, reason):
        """Reject payment"""
        self.status = 'REJETE'
        self.verified_by = admin_user
        self.verified_at = timezone.now()
        self.admin_notes = reason
        self.save()