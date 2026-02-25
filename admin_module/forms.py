"""
Admin Module Forms
COMPLETE VERSION
"""
from django import forms
from client_module.models import Quote, Payment
from core.models import Product, Category, User


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
        label='Document du devis (PDF)',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'accept': '.pdf'
        })
    )
    
    class Meta:
        model = Quote
        fields = [
            'quote_amount_usd', 
            'currency_code', 
            'quote_amount_local', 
            'description', 
            'delivery_time_days', 
            'valid_until',
            'quote_document'
        ]


class ProductForm(forms.ModelForm):
    """Form for product management"""
    
    name = forms.CharField(
        label='Nom du Produit',
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': 'Nom du produit'
        })
    )
    
    description = forms.CharField(
        label='Description',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': 'Description détaillée du produit...',
            'rows': 4
        })
    )
    
    price_usd = forms.DecimalField(
        label='Prix (USD)',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': '0.00',
            'step': '0.01'
        })
    )

    discount_price_usd = forms.DecimalField(
        label='Prix Promotionnel (USD)',
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': '0.00 (optionnel)',
            'step': '0.01'
        })
    )
    
    category = forms.ModelChoiceField(
        label='Catégorie',
        queryset=Category.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition'
        })
    )
    
    stock_quantity = forms.IntegerField(
        label='Quantité en Stock',
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': '0'
        })
    )
    
    image = forms.ImageField(
        label='Image du Produit',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'w-full text-sm text-gray-800',
            'accept': 'image/*'
        })
    )
    
    class Meta:
        model = Product
        fields = ['name', 'description', 'price_usd', 'category', 'stock_quantity', 'image', 'featured', 'is_active']


class CategoryForm(forms.ModelForm):
    """Form for creating/editing categories"""
    
    class Meta:
        model = Category
        fields = ['name', 'icon', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
                'placeholder': 'Nom de la catégorie'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
                'placeholder': 'Icône (ex: 📱)'
            }),
        }


class UserRoleForm(forms.ModelForm):
    """Form for changing user role"""
    
    class Meta:
        model = User
        fields = ['role', 'is_active']
        widgets = {
            'role': forms.Select(attrs={
                'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition'
            }),
        }