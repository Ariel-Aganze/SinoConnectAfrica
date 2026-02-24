"""
Admin Module Forms
"""
from django import forms
from client_module.models import Quote, Payment


class QuoteForm(forms.ModelForm):
    """Form for creating quotes"""
    
    quote_amount_usd = forms.DecimalField(
        label='Montant (USD)',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': '1000.00',
            'step': '0.01'
        })
    )
    
    currency_code = forms.CharField(
        label='Code devise',
        max_length=3,
        initial='XAF',
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': 'XAF'
        })
    )
    
    quote_amount_local = forms.DecimalField(
        label='Montant local',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': '600000.00',
            'step': '0.01'
        })
    )
    
    description = forms.CharField(
        label='Description du devis',
        widget=forms.Textarea(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': 'Détails du devis, ce qui est inclus, conditions...',
            'rows': 4
        })
    )
    
    delivery_time_days = forms.IntegerField(
        label='Délai de livraison (jours)',
        widget=forms.NumberInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': '30'
        })
    )
    
    valid_until = forms.DateField(
        label='Valide jusqu\'au',
        widget=forms.DateInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'type': 'date'
        })
    )
    
    quote_document = forms.FileField(
        label='Document de devis (optionnel)',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'w-full text-sm text-gray-800',
            'accept': '.pdf,.doc,.docx'
        })
    )
    
    class Meta:
        model = Quote
        fields = ['quote_amount_usd', 'currency_code', 'quote_amount_local', 'description', 'delivery_time_days', 'valid_until', 'quote_document']


class PaymentVerificationForm(forms.ModelForm):
    """Form for payment verification"""
    
    admin_notes = forms.CharField(
        label='Notes administrateur',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': 'Notes sur la vérification du paiement...',
            'rows': 3
        })
    )
    
    class Meta:
        model = Payment
        fields = ['admin_notes']