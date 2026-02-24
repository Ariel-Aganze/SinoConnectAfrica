"""
Client Module Forms
"""
from django import forms
from .models import Order, SourcingRequest, Payment


class CheckoutForm(forms.ModelForm):
    """Checkout form for creating orders"""
    
    delivery_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': 'Adresse complète de livraison...',
            'rows': 3
        })
    )
    
    delivery_city = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': 'Brazzaville, Pointe-Noire, Kinshasa...'
        })
    )
    
    delivery_phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': '+242 XX XXX XXXX'
        })
    )
    
    customer_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': 'Instructions spéciales, préférences de livraison...',
            'rows': 3
        })
    )
    
    class Meta:
        model = Order
        fields = ['delivery_address', 'delivery_city', 'delivery_phone', 'customer_notes']


class SourcingRequestForm(forms.ModelForm):
    """Form for creating sourcing requests"""
    
    product_name = forms.CharField(
        label='Nom du produit',
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': 'Ex: Machine de construction, Sacs en cuir...'
        })
    )
    
    product_description = forms.CharField(
        label='Description détaillée',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': 'Décrivez le produit en détail (spécifications, couleur, matériau, etc.)',
            'rows': 4
        })
    )
    
    quantity = forms.IntegerField(
        label='Quantité',
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': 'Ex: 50'
        })
    )
    
    budget = forms.DecimalField(
        label='Budget (USD)',
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': 'Budget total estimé (optionnel)',
            'step': '0.01'
        })
    )
    
    reference_url = forms.URLField(
        label='Lien de référence (Alibaba, Taobao, etc.)',
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': 'https://...'
        })
    )
    
    image = forms.ImageField(
        label='Photo du produit',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'w-full text-sm text-gray-800',
            'accept': 'image/*'
        })
    )
    
    class Meta:
        model = SourcingRequest
        fields = ['product_name', 'product_description', 'quantity', 'budget', 'reference_url', 'image']


class PaymentProofForm(forms.ModelForm):
    """Form for uploading payment proof"""
    
    method = forms.ChoiceField(
        label='Méthode de paiement',
        choices=Payment.METHOD_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition'
        })
    )
    
    transaction_reference = forms.CharField(
        label='Référence de transaction',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': 'Numéro de transaction, reçu, etc.'
        })
    )
    
    proof_image = forms.ImageField(
        label='Preuve de paiement (capture d\'écran, photo)',
        widget=forms.FileInput(attrs={
            'class': 'w-full text-sm text-gray-800',
            'accept': 'image/*'
        })
    )
    
    notes = forms.CharField(
        label='Notes additionnelles',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': 'Informations complémentaires sur le paiement...',
            'rows': 3
        })
    )
    
    class Meta:
        model = Payment
        fields = ['method', 'transaction_reference', 'proof_image', 'notes']