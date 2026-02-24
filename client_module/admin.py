"""
Client Module Admin Configuration
"""
from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, SourcingRequest, Quote, Payment


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Cart admin"""
    list_display = ['user', 'created_at', 'updated_at', 'get_total_items']
    search_fields = ['user__email', 'user__full_name']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Total Items'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Cart Item admin"""
    list_display = ['cart', 'product', 'quantity', 'added_at']
    list_filter = ['added_at']
    search_fields = ['cart__user__email', 'product__name']
    readonly_fields = ['added_at']


class OrderItemInline(admin.TabularInline):
    """Inline for order items"""
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'quantity', 'unit_price_usd']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Order admin"""
    list_display = ['order_code', 'user', 'status', 'total_amount_local', 'currency_code', 'created_at']
    list_filter = ['status', 'created_at', 'currency_code']
    search_fields = ['order_code', 'user__email', 'user__full_name']
    readonly_fields = ['order_code', 'created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('order_code', 'user', 'status')
        }),
        ('Pricing', {
            'fields': ('total_amount_usd', 'currency_code', 'total_amount_local')
        }),
        ('Livraison', {
            'fields': ('delivery_address', 'delivery_city', 'delivery_phone')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at')
        }),
    )


@admin.register(SourcingRequest)
class SourcingRequestAdmin(admin.ModelAdmin):
    """Sourcing Request admin"""
    list_display = ['request_code', 'user', 'product_name', 'quantity', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['request_code', 'user__email', 'user__full_name', 'product_name']
    readonly_fields = ['request_code', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('request_code', 'user', 'status')
        }),
        ('Détails du produit', {
            'fields': ('product_name', 'product_description', 'quantity', 'budget', 'image', 'reference_url')
        }),
        ('Réponse admin', {
            'fields': ('admin_notes', 'estimated_delivery_days')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    """Quote admin"""
    list_display = ['sourcing_request', 'quote_amount_local', 'currency_code', 'accepted', 'created_at']
    list_filter = ['accepted', 'created_at', 'currency_code']
    search_fields = ['sourcing_request__request_code', 'sourcing_request__user__email']
    readonly_fields = ['created_at', 'updated_at', 'accepted_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('sourcing_request', 'admin')
        }),
        ('Détails du devis', {
            'fields': ('quote_amount_usd', 'currency_code', 'quote_amount_local', 'description', 'delivery_time_days', 'valid_until')
        }),
        ('Documents', {
            'fields': ('quote_document',)
        }),
        ('Statut', {
            'fields': ('accepted', 'accepted_at')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Payment admin"""
    list_display = ['order', 'user', 'amount', 'method', 'status', 'created_at']
    list_filter = ['status', 'method', 'created_at']
    search_fields = ['order__order_code', 'user__email', 'transaction_reference']
    readonly_fields = ['created_at', 'updated_at', 'verified_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('order', 'user', 'amount', 'method', 'status')
        }),
        ('Preuve de paiement', {
            'fields': ('proof_image', 'transaction_reference', 'notes')
        }),
        ('Vérification', {
            'fields': ('verified_by', 'verified_at', 'admin_notes')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )