"""
Client Module Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q
from django.utils import timezone
from core.models import Product, Currency, Notification
from .models import Cart, CartItem, Order, OrderItem, SourcingRequest, Quote, Payment
from .forms import CheckoutForm, SourcingRequestForm, PaymentProofForm


def client_required(view_func):
    """Decorator to ensure user is a client"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'CLIENT':
            messages.error(request, 'Accès refusé. Cette page est réservée aux clients.')
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@client_required
def dashboard(request):
    """Client dashboard"""
    user = request.user
    
    # Statistics
    total_orders = user.orders.count()
    pending_orders = user.orders.filter(status__in=['EN_ATTENTE', 'PAYE', 'PREPARATION']).count()
    completed_orders = user.orders.filter(status='LIVRE').count()
    
    # Recent orders
    recent_orders = user.orders.all()[:5]
    
    # Sourcing requests
    sourcing_requests = user.sourcing_requests.all()[:5]
    pending_sourcing = user.sourcing_requests.filter(status__in=['EN_ATTENTE', 'EN_COURS']).count()
    
    # Agent info
    agent_assignment = getattr(user, 'agent_assignment', None)
    
    # Recent notifications
    notifications = user.notifications.all()[:5]
    
    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'recent_orders': recent_orders,
        'sourcing_requests': sourcing_requests,
        'pending_sourcing': pending_sourcing,
        'agent_assignment': agent_assignment,
        'notifications': notifications,
    }
    return render(request, 'client_module/dashboard.html', context)


@login_required
@client_required
def cart_view(request):
    """Shopping cart view"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product').all()
    
    # Get selected currency
    currency_code = request.session.get('currency', 'USD')
    currency = Currency.objects.filter(code=currency_code).first() or Currency.get_base_currency()
    
    total_price = cart.get_total_price(currency)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price,
        'currency': currency,
    }
    return render(request, 'client_module/cart.html', context)


@login_required
@client_required
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Check if product already in cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        # Increment quantity
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f'Quantité de "{product.name}" augmentée dans le panier.')
    else:
        messages.success(request, f'"{product.name}" ajouté au panier.')
    
    # Redirect to previous page or cart
    next_url = request.GET.get('next', 'client_module:cart')
    return redirect(next_url)


@login_required
@client_required
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Quantité mise à jour.')
        else:
            cart_item.delete()
            messages.success(request, 'Article retiré du panier.')
    
    return redirect('client_module:cart')


@login_required
@client_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    
    messages.success(request, f'"{product_name}" retiré du panier.')
    return redirect('client_module:cart')


@login_required
@client_required
def checkout(request):
    """Checkout process"""
    cart = get_object_or_404(Cart, user=request.user)
    
    if not cart.items.exists():
        messages.warning(request, 'Votre panier est vide.')
        return redirect('client_module:cart')
    
    # Get selected currency
    currency_code = request.session.get('currency', 'USD')
    currency = Currency.objects.filter(code=currency_code).first() or Currency.get_base_currency()
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order
            order = form.save(commit=False)
            order.user = request.user
            order.currency_code = currency.code
            order.total_amount_local = cart.get_total_price(currency)
            order.total_amount_usd = cart.get_total_price(Currency.get_base_currency())
            order.save()
            
            # Create order items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    quantity=cart_item.quantity,
                    unit_price_usd=cart_item.product.price_usd
                )
            
            # Clear cart
            cart.clear()
            
            # Create notification
            Notification.objects.create(
                user=request.user,
                type='COMMANDE',
                title='Commande créée',
                message=f'Votre commande {order.order_code} a été créée avec succès. Veuillez procéder au paiement.',
                link=f'/client/orders/{order.id}/'
            )
            
            messages.success(request, f'Commande {order.order_code} créée avec succès!')
            return redirect('client_module:order_detail', order_id=order.id)
    else:
        # Pre-fill form with user data
        initial_data = {
            'delivery_city': request.user.city,
            'delivery_phone': request.user.phone_number,
        }
        form = CheckoutForm(initial=initial_data)
    
    total_price = cart.get_total_price(currency)
    
    context = {
        'form': form,
        'cart': cart,
        'total_price': total_price,
        'currency': currency,
    }
    return render(request, 'client_module/checkout.html', context)


@login_required
@client_required
def order_list(request):
    """List of user orders"""
    orders = request.user.orders.all()
    
    # Filters
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    # Pagination
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    orders_page = paginator.get_page(page_number)
    
    context = {
        'orders': orders_page,
        'selected_status': status,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'client_module/order_list.html', context)


@login_required
@client_required
def order_detail(request, order_id):
    """Order detail view"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.select_related('product').all()
    payments = order.payments.all()
    
    # Get currency
    currency = Currency.objects.filter(code=order.currency_code).first() or Currency.get_base_currency()
    
    context = {
        'order': order,
        'order_items': order_items,
        'payments': payments,
        'currency': currency,
    }
    return render(request, 'client_module/order_detail.html', context)


@login_required
@client_required
def upload_payment_proof(request, order_id):
    """Upload payment proof"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        form = PaymentProofForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.order = order
            payment.user = request.user
            payment.amount = order.total_amount_local
            payment.save()
            
            # Create notification
            Notification.objects.create(
                user=request.user,
                type='PAYMENT',
                title='Preuve de paiement envoyée',
                message=f'Votre preuve de paiement pour {order.order_code} a été envoyée. En attente de vérification.',
                link=f'/client/orders/{order.id}/'
            )
            
            messages.success(request, 'Preuve de paiement envoyée avec succès!')
            return redirect('client_module:order_detail', order_id=order.id)
    else:
        form = PaymentProofForm()
    
    context = {
        'form': form,
        'order': order,
    }
    return render(request, 'client_module/upload_payment_proof.html', context)


@login_required
@client_required
def sourcing_request_list(request):
    """List of sourcing requests"""
    sourcing_requests = request.user.sourcing_requests.all()
    
    # Filters
    status = request.GET.get('status')
    if status:
        sourcing_requests = sourcing_requests.filter(status=status)
    
    # Pagination
    paginator = Paginator(sourcing_requests, 10)
    page_number = request.GET.get('page')
    requests_page = paginator.get_page(page_number)
    
    context = {
        'sourcing_requests': requests_page,
        'selected_status': status,
        'status_choices': SourcingRequest.STATUS_CHOICES,
    }
    return render(request, 'client_module/sourcing_request_list.html', context)


@login_required
@client_required
def sourcing_request_create(request):
    """Create new sourcing request"""
    if request.method == 'POST':
        form = SourcingRequestForm(request.POST, request.FILES)
        if form.is_valid():
            sourcing_request = form.save(commit=False)
            sourcing_request.user = request.user
            sourcing_request.save()
            
            # Create notification
            Notification.objects.create(
                user=request.user,
                type='SOURCING',
                title='Demande de sourcing créée',
                message=f'Votre demande {sourcing_request.request_code} a été créée. Notre équipe va la traiter rapidement.',
                link=f'/client/sourcing/{sourcing_request.id}/'
            )
            
            messages.success(request, f'Demande de sourcing {sourcing_request.request_code} créée avec succès!')
            return redirect('client_module:sourcing_request_detail', request_id=sourcing_request.id)
    else:
        form = SourcingRequestForm()
    
    context = {
        'form': form,
    }
    return render(request, 'client_module/sourcing_request_create.html', context)


@login_required
@client_required
def sourcing_request_detail(request, request_id):
    """Sourcing request detail"""
    sourcing_request = get_object_or_404(SourcingRequest, id=request_id, user=request.user)
    quotes = sourcing_request.quotes.all()
    
    context = {
        'sourcing_request': sourcing_request,
        'quotes': quotes,
    }
    return render(request, 'client_module/sourcing_request_detail.html', context)


@login_required
@client_required
def accept_quote(request, quote_id):
    """Accept a quote"""
    quote = get_object_or_404(Quote, id=quote_id, sourcing_request__user=request.user)
    
    if request.method == 'POST':
        quote.accept()
        
        # Create notification
        Notification.objects.create(
            user=request.user,
            type='SOURCING',
            title='Devis accepté',
            message=f'Vous avez accepté le devis pour {quote.sourcing_request.request_code}. Notre équipe va commencer le processus.',
            link=f'/client/sourcing/{quote.sourcing_request.id}/'
        )
        
        messages.success(request, 'Devis accepté! Notre équipe va vous contacter pour finaliser la commande.')
        return redirect('client_module:sourcing_request_detail', request_id=quote.sourcing_request.id)
    
    context = {
        'quote': quote,
    }
    return render(request, 'client_module/accept_quote.html', context)


@login_required
@client_required
def my_agent(request):
    """View assigned agent"""
    agent_assignment = getattr(request.user, 'agent_assignment', None)
    
    context = {
        'agent_assignment': agent_assignment,
    }
    return render(request, 'client_module/my_agent.html', context)