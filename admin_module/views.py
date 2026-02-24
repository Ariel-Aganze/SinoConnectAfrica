"""
Admin Module Views - Platform Management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from core.models import User, Product, Category, Currency, Notification
from client_module.models import Order, SourcingRequest, Quote, Payment
from .forms import QuoteForm, PaymentVerificationForm


def admin_required(view_func):
    """Decorator to ensure user is admin"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'ADMIN':
            messages.error(request, 'Accès refusé. Cette page est réservée aux administrateurs.')
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@admin_required
def dashboard(request):
    """Admin dashboard with analytics"""
    
    # Time periods
    today = timezone.now()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)
    
    # User statistics
    total_users = User.objects.filter(role='CLIENT').count()
    new_users_30d = User.objects.filter(role='CLIENT', created_at__gte=last_30_days).count()
    total_agents = User.objects.filter(role='AGENT').count()
    
    # Order statistics
    all_orders = Order.objects.all()
    total_orders = all_orders.count()
    pending_orders = all_orders.filter(status__in=['EN_ATTENTE', 'PAYE', 'PREPARATION']).count()
    orders_30d = all_orders.filter(created_at__gte=last_30_days).count()
    
    # Revenue (in USD)
    total_revenue = all_orders.filter(status__in=['PAYE', 'PREPARATION', 'EXPEDIE', 'EN_TRANSIT', 'LIVRE']).aggregate(
        total=Sum('total_amount_usd')
    )['total'] or 0
    revenue_30d = all_orders.filter(
        status__in=['PAYE', 'PREPARATION', 'EXPEDIE', 'EN_TRANSIT', 'LIVRE'],
        created_at__gte=last_30_days
    ).aggregate(total=Sum('total_amount_usd'))['total'] or 0
    
    # Sourcing statistics
    total_sourcing = SourcingRequest.objects.count()
    pending_sourcing = SourcingRequest.objects.filter(status__in=['EN_ATTENTE', 'EN_COURS']).count()
    
    # Payment verification needed
    pending_payments = Payment.objects.filter(status='EN_ATTENTE').count()
    
    # Product statistics
    total_products = Product.objects.filter(is_active=True).count()
    out_of_stock = Product.objects.filter(stock_status='OUT_OF_STOCK').count()
    
    # Recent activity
    recent_orders = all_orders.order_by('-created_at')[:5]
    recent_sourcing = SourcingRequest.objects.order_by('-created_at')[:5]
    recent_users = User.objects.filter(role='CLIENT').order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'new_users_30d': new_users_30d,
        'total_agents': total_agents,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'orders_30d': orders_30d,
        'total_revenue': total_revenue,
        'revenue_30d': revenue_30d,
        'total_sourcing': total_sourcing,
        'pending_sourcing': pending_sourcing,
        'pending_payments': pending_payments,
        'total_products': total_products,
        'out_of_stock': out_of_stock,
        'recent_orders': recent_orders,
        'recent_sourcing': recent_sourcing,
        'recent_users': recent_users,
    }
    return render(request, 'admin_module/dashboard.html', context)


@login_required
@admin_required
def order_management(request):
    """Order management interface"""
    orders = Order.objects.all().select_related('user')
    
    # Filters
    status = request.GET.get('status')
    search = request.GET.get('search')
    
    if status:
        orders = orders.filter(status=status)
    if search:
        orders = orders.filter(
            Q(order_code__icontains=search) |
            Q(user__full_name__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    orders = orders.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    orders_page = paginator.get_page(page_number)
    
    context = {
        'orders': orders_page,
        'selected_status': status,
        'search_query': search,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'admin_module/order_management.html', context)


@login_required
@admin_required
def order_detail_admin(request, order_id):
    """Admin order detail with status update"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            old_status = order.status
            order.status = new_status
            order.save()
            
            # Create notification for client
            Notification.objects.create(
                user=order.user,
                type='COMMANDE',
                title='Statut de commande mis à jour',
                message=f'Votre commande {order.order_code} est maintenant: {order.get_status_display()}',
                link=f'/client/orders/{order.id}/'
            )
            
            messages.success(request, f'Statut mis à jour: {order.get_status_display()}')
            return redirect('admin_module:order_detail_admin', order_id=order.id)
    
    order_items = order.items.select_related('product').all()
    payments = order.payments.all()
    
    context = {
        'order': order,
        'order_items': order_items,
        'payments': payments,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'admin_module/order_detail_admin.html', context)


@login_required
@admin_required
def sourcing_management(request):
    """Sourcing request management"""
    sourcing_requests = SourcingRequest.objects.all().select_related('user')
    
    # Filters
    status = request.GET.get('status')
    if status:
        sourcing_requests = sourcing_requests.filter(status=status)
    
    sourcing_requests = sourcing_requests.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(sourcing_requests, 20)
    page_number = request.GET.get('page')
    requests_page = paginator.get_page(page_number)
    
    context = {
        'sourcing_requests': requests_page,
        'selected_status': status,
        'status_choices': SourcingRequest.STATUS_CHOICES,
    }
    return render(request, 'admin_module/sourcing_management.html', context)


@login_required
@admin_required
def sourcing_detail_admin(request, request_id):
    """Admin sourcing detail with quote creation"""
    sourcing_request = get_object_or_404(SourcingRequest, id=request_id)
    quotes = sourcing_request.quotes.all()
    
    if request.method == 'POST':
        # Update status
        if 'update_status' in request.POST:
            new_status = request.POST.get('status')
            sourcing_request.status = new_status
            sourcing_request.admin_notes = request.POST.get('admin_notes', '')
            sourcing_request.save()
            messages.success(request, 'Statut mis à jour')
            return redirect('admin_module:sourcing_detail_admin', request_id=request_id)
    
    context = {
        'sourcing_request': sourcing_request,
        'quotes': quotes,
        'status_choices': SourcingRequest.STATUS_CHOICES,
    }
    return render(request, 'admin_module/sourcing_detail_admin.html', context)


@login_required
@admin_required
def create_quote(request, request_id):
    """Create quote for sourcing request"""
    sourcing_request = get_object_or_404(SourcingRequest, id=request_id)
    
    if request.method == 'POST':
        form = QuoteForm(request.POST, request.FILES)
        if form.is_valid():
            quote = form.save(commit=False)
            quote.sourcing_request = sourcing_request
            quote.admin = request.user
            quote.save()
            
            # Update sourcing request status
            sourcing_request.status = 'DEVIS_ENVOYE'
            sourcing_request.save()
            
            # Notify client
            Notification.objects.create(
                user=sourcing_request.user,
                type='SOURCING',
                title='Devis reçu',
                message=f'Un devis est disponible pour votre demande {sourcing_request.request_code}',
                link=f'/client/sourcing/{sourcing_request.id}/'
            )
            
            messages.success(request, 'Devis créé et envoyé au client')
            return redirect('admin_module:sourcing_detail_admin', request_id=request_id)
    else:
        form = QuoteForm()
    
    context = {
        'form': form,
        'sourcing_request': sourcing_request,
    }
    return render(request, 'admin_module/create_quote.html', context)


@login_required
@admin_required
def payment_verification(request):
    """Payment verification interface"""
    payments = Payment.objects.filter(status='EN_ATTENTE').select_related('order', 'user')
    
    # Pagination
    paginator = Paginator(payments, 20)
    page_number = request.GET.get('page')
    payments_page = paginator.get_page(page_number)
    
    context = {
        'payments': payments_page,
    }
    return render(request, 'admin_module/payment_verification.html', context)


@login_required
@admin_required
def verify_payment(request, payment_id):
    """Verify or reject payment"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            payment.confirm(request.user)
            messages.success(request, 'Paiement confirmé')
        elif action == 'reject':
            reason = request.POST.get('reason', 'Preuve de paiement invalide')
            payment.reject(request.user, reason)
            messages.warning(request, 'Paiement rejeté')
        
        return redirect('admin_module:payment_verification')
    
    context = {
        'payment': payment,
    }
    return render(request, 'admin_module/verify_payment.html', context)


@login_required
@admin_required
def user_management(request):
    """User management interface"""
    users = User.objects.all()
    
    # Filters
    role = request.GET.get('role')
    search = request.GET.get('search')
    
    if role:
        users = users.filter(role=role)
    if search:
        users = users.filter(
            Q(full_name__icontains=search) |
            Q(email__icontains=search) |
            Q(city__icontains=search)
        )
    
    users = users.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)
    
    context = {
        'users': users_page,
        'selected_role': role,
        'search_query': search,
    }
    return render(request, 'admin_module/user_management.html', context)