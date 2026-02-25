"""
Admin Module Views - Platform Management
COMPLETE AND FIXED VERSION
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
from .forms import QuoteForm
from django.http import JsonResponse



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
    search = request.GET.get('search')
    
    if status:
        sourcing_requests = sourcing_requests.filter(status=status)
    if search:
        sourcing_requests = sourcing_requests.filter(
            Q(request_code__icontains=search) |
            Q(user__full_name__icontains=search) |
            Q(product_name__icontains=search)
        )
    
    sourcing_requests = sourcing_requests.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(sourcing_requests, 20)
    page_number = request.GET.get('page')
    requests_page = paginator.get_page(page_number)
    
    context = {
        'sourcing_requests': requests_page,
        'selected_status': status,
        'search_query': search,
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
            
            # Create notification for client
            Notification.objects.create(
                user=sourcing_request.user,
                type='SOURCING',
                title='Statut de demande mis à jour',
                message=f'Votre demande {sourcing_request.request_code} a été mise à jour: {sourcing_request.get_status_display()}',
                link=f'/client/sourcing/{sourcing_request.id}/'
            )
            
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
    
    # Filters
    search = request.GET.get('search')
    if search:
        payments = payments.filter(
            Q(order__order_code__icontains=search) |
            Q(user__full_name__icontains=search) |
            Q(transaction_reference__icontains=search)
        )
    
    payments = payments.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(payments, 20)
    page_number = request.GET.get('page')
    payments_page = paginator.get_page(page_number)
    
    context = {
        'payments': payments_page,
        'search_query': search,
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
            
            # Create notification for client
            Notification.objects.create(
                user=payment.user,
                type='PAIEMENT',
                title='Paiement confirmé',
                message=f'Votre paiement pour la commande {payment.order.order_code} a été confirmé',
                link=f'/client/orders/{payment.order.id}/'
            )
            
            messages.success(request, 'Paiement confirmé avec succès')
            
        elif action == 'reject':
            reason = request.POST.get('reason', 'Preuve de paiement invalide')
            payment.reject(request.user, reason)
            
            # Create notification for client
            Notification.objects.create(
                user=payment.user,
                type='PAIEMENT',
                title='Paiement rejeté',
                message=f'Votre paiement pour la commande {payment.order.order_code} a été rejeté. Raison: {reason}',
                link=f'/client/orders/{payment.order.id}/'
            )
            
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
    city = request.GET.get('city')
    
    if role:
        users = users.filter(role=role)
    if search:
        users = users.filter(
            Q(full_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone_number__icontains=search)
        )
    if city:
        users = users.filter(city__icontains=city)
    
    users = users.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)
    
    # Get all cities for filter
    cities = User.objects.exclude(city__isnull=True).exclude(city='').values_list('city', flat=True).distinct()
    
    context = {
        'users': users_page,
        'selected_role': role,
        'search_query': search,
        'selected_city': city,
        'cities': cities,
        'role_choices': User.ROLE_CHOICES,
    }
    return render(request, 'admin_module/user_management.html', context)


@login_required
@admin_required
def user_detail_admin(request, user_id):
    """Admin view of user details"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'toggle_active':
            user.is_active = not user.is_active
            user.save()
            status = 'activé' if user.is_active else 'désactivé'
            messages.success(request, f'Compte {status} avec succès')
            
        elif action == 'change_role':
            new_role = request.POST.get('role')
            if new_role in dict(User.ROLE_CHOICES):
                user.role = new_role
                user.save()
                messages.success(request, f'Rôle modifié à {user.get_role_display()}')
        
        return redirect('admin_module:user_detail_admin', user_id=user_id)
    
    # Get user statistics
    if user.role == 'CLIENT':
        orders = user.orders.all()
        total_orders = orders.count()
        total_spent = orders.filter(
            status__in=['PAYE', 'PREPARATION', 'EXPEDIE', 'EN_TRANSIT', 'LIVRE']
        ).aggregate(total=Sum('total_amount_usd'))['total'] or 0
        
        sourcing_requests = user.sourcing_requests.all()
        
        context = {
            'user': user,
            'orders': orders[:10],
            'total_orders': total_orders,
            'total_spent': total_spent,
            'sourcing_requests': sourcing_requests[:10],
        }
    elif user.role == 'AGENT':
        from core.models import AgentAssignment
        assignments = AgentAssignment.objects.filter(agent=user).select_related('client')
        
        context = {
            'user': user,
            'assignments': assignments,
        }
    else:
        context = {
            'user': user,
        }
    
    return render(request, 'admin_module/user_detail_admin.html', context)


@login_required
@admin_required
def product_management(request):
    """Product management view with CRUD operations and statistics"""
    from core.models import Product, Category
    from django.db.models import Q, Count
    from django.core.files.storage import default_storage
    import os
    
    # Handle POST requests (Save/Update/Toggle)
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save_product':
            product_id = request.POST.get('product_id')
            
            # Get or create product
            if product_id:
                product = get_object_or_404(Product, id=product_id)
                message = 'Produit modifié avec succès'
            else:
                product = Product()
                message = 'Produit créé avec succès'
            
            # Update fields
            product.name = request.POST.get('name')
            product.description = request.POST.get('description')
            product.price_usd = request.POST.get('price_usd')
            product.stock_quantity = request.POST.get('stock_quantity', 0)
            product.stock_status = request.POST.get('stock_status', 'IN_STOCK')
            product.featured = request.POST.get('featured') == 'on'
            product.is_active = request.POST.get('is_active') == 'on'
            
            # IMPORTANT: Handle discount_price_usd
            discount_price = request.POST.get('discount_price_usd')
            if discount_price and discount_price.strip():
                product.discount_price_usd = discount_price
            else:
                product.discount_price_usd = None
            
            # Handle category
            category_id = request.POST.get('category')
            if category_id:
                product.category_id = category_id
            else:
                product.category = None
            
            # Generate slug from name if new product
            if not product_id:
                from django.utils.text import slugify
                base_slug = slugify(product.name)
                slug = base_slug
                counter = 1
                while Product.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                product.slug = slug
            
            # Handle main image upload
            if request.FILES.get('image'):
                product.image = request.FILES['image']
            
            # Save product first to get an ID
            product.save()
            
            # Handle additional images (multiple files)
            additional_files = request.FILES.getlist('additional_images')
            if additional_files:
                additional_images_urls = []
                
                # Keep existing additional images if editing
                if product.additional_images:
                    additional_images_urls = product.additional_images
                
                # Limit to 5 additional images total
                max_additional = 5 - len(additional_images_urls)
                
                for i, file in enumerate(additional_files[:max_additional]):
                    # Generate unique filename
                    ext = os.path.splitext(file.name)[1]
                    filename = f"products/additional/{product.id}_{i}_{file.name}"
                    
                    # Save file
                    path = default_storage.save(filename, file)
                    url = default_storage.url(path)
                    additional_images_urls.append(url)
                
                product.additional_images = additional_images_urls
                product.save()
            
            messages.success(request, message)
            return redirect('admin_module:product_management')
        
        elif action == 'toggle_status':
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            product.is_active = not product.is_active
            product.save()
            
            status = 'activé' if product.is_active else 'désactivé'
            messages.success(request, f'Produit {status} avec succès')
            return redirect('admin_module:product_management')
    
    # GET request - Display products
    products = Product.objects.all().select_related('category')
    categories = Category.objects.filter(is_active=True).order_by('name')
    
    # Filters
    category = request.GET.get('category')
    search = request.GET.get('search')
    stock_status = request.GET.get('stock_status')
    
    if category:
        products = products.filter(category_id=category)
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    if stock_status:
        products = products.filter(stock_status=stock_status)
    
    products = products.order_by('-created_at')
    
    # Calculate statistics
    all_products = Product.objects.all()
    in_stock_count = all_products.filter(stock_status='IN_STOCK').count()
    on_order_count = all_products.filter(stock_status='ON_ORDER').count()
    out_of_stock_count = all_products.filter(stock_status='OUT_OF_STOCK').count()
    featured_count = all_products.filter(featured=True).count()
    
    # Pagination
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)
    
    context = {
        'products': products_page,
        'categories': categories,
        'selected_category': category,
        'search_query': search,
        'selected_stock_status': stock_status,
        'stock_status_choices': Product.STOCK_STATUS_CHOICES,
        'in_stock_count': in_stock_count,
        'on_order_count': on_order_count,
        'out_of_stock_count': out_of_stock_count,
        'featured_count': featured_count,
    }
    return render(request, 'admin_module/product_management.html', context)



@login_required
@admin_required
def get_product_data(request, product_id):
    """Get product data as JSON for editing"""
    try:
        product = get_object_or_404(Product, id=product_id)
        
        data = {
            'success': True,
            'product': {
                'id': str(product.id),
                'name': product.name,
                'description': product.description,
                'price_usd': str(product.price_usd),
                'discount_price_usd': str(product.discount_price_usd) if product.discount_price_usd else '',
                'category_id': str(product.category.id) if product.category else None,
                'stock_quantity': product.stock_quantity,
                'stock_status': product.stock_status,
                'featured': product.featured,
                'is_active': product.is_active,
                'image': product.image.url if product.image else None,
                'additional_images': product.additional_images if product.additional_images else [],
            }
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@admin_required
def category_management(request):
    """Category management view with CRUD operations"""
    from core.models import Category, Product
    from django.db.models import Q
    from django.utils.text import slugify
    
    # Handle POST requests (Save/Update/Toggle/Delete)
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save_category':
            category_id = request.POST.get('category_id')
            
            # Get or create category
            if category_id:
                category = get_object_or_404(Category, id=category_id)
                message = 'Catégorie modifiée avec succès'
            else:
                category = Category()
                message = 'Catégorie créée avec succès'
            
            # Update fields
            category.name = request.POST.get('name')
            category.icon = request.POST.get('icon', '📦')
            category.description = request.POST.get('description', '')
            category.is_active = request.POST.get('is_active') == 'on'
            
            # Generate slug from name
            base_slug = slugify(category.name)
            slug = base_slug
            counter = 1
            
            # Check for existing slug (exclude current category if editing)
            while True:
                existing = Category.objects.filter(slug=slug)
                if category_id:
                    existing = existing.exclude(id=category_id)
                
                if not existing.exists():
                    break
                    
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            category.slug = slug
            category.save()
            
            messages.success(request, message)
            return redirect('admin_module:category_management')
        
        elif action == 'toggle_status':
            category_id = request.POST.get('category_id')
            category = get_object_or_404(Category, id=category_id)
            category.is_active = not category.is_active
            category.save()
            
            status = 'activée' if category.is_active else 'désactivée'
            messages.success(request, f'Catégorie {status} avec succès')
            return redirect('admin_module:category_management')
        
        elif action == 'delete_category':
            category_id = request.POST.get('category_id')
            category = get_object_or_404(Category, id=category_id)
            
            # Check if category has products
            if category.products.count() > 0:
                messages.error(request, 'Impossible de supprimer une catégorie contenant des produits')
            else:
                category_name = category.name
                category.delete()
                messages.success(request, f'Catégorie "{category_name}" supprimée avec succès')
            
            return redirect('admin_module:category_management')
    
    # GET request - Display categories
    categories = Category.objects.all()
    
    # Search filter
    search = request.GET.get('search')
    if search:
        categories = categories.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    categories = categories.prefetch_related('products').order_by('name')
    
    # Statistics
    active_categories = categories.filter(is_active=True).count()
    total_products = Product.objects.count()
    
    # Calculate average products per category
    avg_products_per_category = 0
    if categories.count() > 0:
        avg_products_per_category = total_products / categories.count()
    
    context = {
        'categories': categories,
        'search_query': search,
        'active_categories': active_categories,
        'total_products': total_products,
        'avg_products_per_category': avg_products_per_category,
    }
    return render(request, 'admin_module/category_management.html', context)


@login_required
@admin_required
def get_category_data(request, category_id):
    """Get category data as JSON for editing"""
    try:
        category = get_object_or_404(Category, id=category_id)
        
        data = {
            'success': True,
            'category': {
                'id': str(category.id),
                'name': category.name,
                'slug': category.slug,
                'icon': category.icon,
                'description': category.description,
                'is_active': category.is_active,
            }
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@admin_required
def analytics(request):
    """Advanced analytics dashboard"""
    # Time periods
    today = timezone.now()
    last_30_days = today - timedelta(days=30)
    last_90_days = today - timedelta(days=90)
    
    # Revenue analytics
    revenue_by_month = Order.objects.filter(
        status__in=['PAYE', 'PREPARATION', 'EXPEDIE', 'EN_TRANSIT', 'LIVRE'],
        created_at__gte=last_90_days
    ).extra(
        select={'month': 'EXTRACT(month FROM created_at)'}
    ).values('month').annotate(
        total=Sum('total_amount_usd')
    ).order_by('month')
    
    # Top products
    from django.db.models import F
    from client_module.models import OrderItem
    
    top_products = OrderItem.objects.filter(
        order__created_at__gte=last_30_days,
        order__status__in=['PAYE', 'PREPARATION', 'EXPEDIE', 'EN_TRANSIT', 'LIVRE']
    ).values(
        'product_name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('unit_price_usd'))
    ).order_by('-total_revenue')[:10]
    
    # Top customers
    top_customers = User.objects.filter(
        role='CLIENT'
    ).annotate(
        total_spent=Sum(
            'orders__total_amount_usd',
            filter=Q(
                orders__status__in=['PAYE', 'PREPARATION', 'EXPEDIE', 'EN_TRANSIT', 'LIVRE'],
                orders__created_at__gte=last_30_days
            )
        ),
        order_count=Count(
            'orders',
            filter=Q(
                orders__status__in=['PAYE', 'PREPARATION', 'EXPEDIE', 'EN_TRANSIT', 'LIVRE'],
                orders__created_at__gte=last_30_days
            )
        )
    ).filter(total_spent__gt=0).order_by('-total_spent')[:10]
    
    context = {
        'revenue_by_month': revenue_by_month,
        'top_products': top_products,
        'top_customers': top_customers,
    }
    return render(request, 'admin_module/analytics.html', context)