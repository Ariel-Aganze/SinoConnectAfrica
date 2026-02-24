"""
Context processors for global template variables
"""
from .models import SiteSettings, Currency


def site_settings(request):
    """Add site settings to all templates"""
    return {
        'site_settings': SiteSettings.get_settings(),
    }


def notifications_processor(request):
    """Add notifications count to all templates"""
    if request.user.is_authenticated:
        unread_count = request.user.get_unread_notifications_count()
        return {
            'unread_notifications_count': unread_count,
        }
    return {
        'unread_notifications_count': 0,
    }


def cart_processor(request):
    """Add cart count to all templates"""
    if request.user.is_authenticated and request.user.role == 'CLIENT':
        try:
            from client_module.models import Cart
            cart = Cart.objects.filter(user=request.user).first()
            if cart:
                return {
                    'cart_count': cart.get_total_items(),
                }
        except:
            pass
    return {
        'cart_count': 0,
    }


def currency_processor(request):
    """Add available currencies to all templates"""
    currencies = Currency.objects.filter(is_active=True)
    base_currency = Currency.get_base_currency()
    
    # Get user's preferred currency from session or use base
    selected_currency_code = request.session.get('currency', base_currency.code if base_currency else 'USD')
    selected_currency = currencies.filter(code=selected_currency_code).first() or base_currency
    
    return {
        'currencies': currencies,
        'selected_currency': selected_currency,
        'base_currency': base_currency,
    }