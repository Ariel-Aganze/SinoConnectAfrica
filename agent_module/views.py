"""
Agent Module Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from core.models import User, AgentAssignment, Notification
from client_module.models import Order, SourcingRequest


def agent_required(view_func):
    """Decorator to ensure user is an agent"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'AGENT':
            messages.error(request, 'Accès refusé. Cette page est réservée aux agents.')
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@agent_required
def dashboard(request):
    """Agent dashboard"""
    agent = request.user
    
    # Get assigned clients
    assignments = AgentAssignment.objects.filter(agent=agent).select_related('client')
    assigned_clients = [a.client for a in assignments]
    client_ids = [c.id for c in assigned_clients]
    
    # Statistics
    total_clients = len(assigned_clients)
    
    # Orders from assigned clients
    all_orders = Order.objects.filter(user_id__in=client_ids)
    total_orders = all_orders.count()
    pending_orders = all_orders.filter(status__in=['EN_ATTENTE', 'PAYE', 'PREPARATION']).count()
    
    # Sourcing requests
    all_sourcing = SourcingRequest.objects.filter(user_id__in=client_ids)
    pending_sourcing = all_sourcing.filter(status__in=['EN_ATTENTE', 'EN_COURS']).count()
    
    # Recent activity
    recent_orders = all_orders.order_by('-created_at')[:5]
    recent_sourcing = all_sourcing.order_by('-created_at')[:5]
    
    context = {
        'total_clients': total_clients,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'pending_sourcing': pending_sourcing,
        'recent_orders': recent_orders,
        'recent_sourcing': recent_sourcing,
        'assigned_clients': assigned_clients[:5],  # Top 5 for dashboard
    }
    return render(request, 'agent_module/dashboard.html', context)


@login_required
@agent_required
def client_list(request):
    """List of assigned clients"""
    agent = request.user
    
    # Get all assigned clients with related data
    assignments = AgentAssignment.objects.filter(agent=agent).select_related('client')
    clients_data = []
    
    for assignment in assignments:
        client = assignment.client
        orders_count = Order.objects.filter(user=client).count()
        pending_orders = Order.objects.filter(user=client, status__in=['EN_ATTENTE', 'PAYE', 'PREPARATION']).count()
        sourcing_count = SourcingRequest.objects.filter(user=client).count()
        
        clients_data.append({
            'client': client,
            'assignment': assignment,
            'orders_count': orders_count,
            'pending_orders': pending_orders,
            'sourcing_count': sourcing_count,
        })
    
    # Pagination
    paginator = Paginator(clients_data, 10)
    page_number = request.GET.get('page')
    clients_page = paginator.get_page(page_number)
    
    context = {
        'clients': clients_page,
    }
    return render(request, 'agent_module/client_list.html', context)


@login_required
@agent_required
def client_detail(request, client_id):
    """Client detail view"""
    agent = request.user
    client = get_object_or_404(User, id=client_id, role='CLIENT')
    
    # Verify this client is assigned to this agent
    assignment = get_object_or_404(AgentAssignment, agent=agent, client=client)
    
    # Get client's orders and sourcing
    orders = Order.objects.filter(user=client).order_by('-created_at')
    sourcing_requests = SourcingRequest.objects.filter(user=client).order_by('-created_at')
    
    # Statistics
    total_orders = orders.count()
    completed_orders = orders.filter(status='LIVRE').count()
    total_sourcing = sourcing_requests.count()
    
    context = {
        'client': client,
        'assignment': assignment,
        'orders': orders[:10],  # Recent 10
        'sourcing_requests': sourcing_requests[:10],  # Recent 10
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'total_sourcing': total_sourcing,
    }
    return render(request, 'agent_module/client_detail.html', context)


@login_required
@agent_required
def order_list(request):
    """List of orders for assigned clients"""
    agent = request.user
    
    # Get client IDs
    assignments = AgentAssignment.objects.filter(agent=agent)
    client_ids = [a.client_id for a in assignments]
    
    # Get orders
    orders = Order.objects.filter(user_id__in=client_ids).select_related('user')
    
    # Filters
    status = request.GET.get('status')
    client_id = request.GET.get('client')
    
    if status:
        orders = orders.filter(status=status)
    if client_id:
        orders = orders.filter(user_id=client_id)
    
    orders = orders.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 15)
    page_number = request.GET.get('page')
    orders_page = paginator.get_page(page_number)
    
    # Get clients for filter
    clients = User.objects.filter(id__in=client_ids)
    
    context = {
        'orders': orders_page,
        'clients': clients,
        'selected_status': status,
        'selected_client': client_id,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'agent_module/order_list.html', context)


@login_required
@agent_required
def order_detail(request, order_id):
    """Order detail view"""
    agent = request.user
    
    # Get order and verify client is assigned to agent
    order = get_object_or_404(Order, id=order_id)
    assignment = get_object_or_404(AgentAssignment, agent=agent, client=order.user)
    
    order_items = order.items.select_related('product').all()
    payments = order.payments.all()
    
    context = {
        'order': order,
        'order_items': order_items,
        'payments': payments,
    }
    return render(request, 'agent_module/order_detail.html', context)


@login_required
@agent_required
def sourcing_list(request):
    """List of sourcing requests for assigned clients"""
    agent = request.user
    
    # Get client IDs
    assignments = AgentAssignment.objects.filter(agent=agent)
    client_ids = [a.client_id for a in assignments]
    
    # Get sourcing requests
    sourcing_requests = SourcingRequest.objects.filter(user_id__in=client_ids).select_related('user')
    
    # Filters
    status = request.GET.get('status')
    if status:
        sourcing_requests = sourcing_requests.filter(status=status)
    
    sourcing_requests = sourcing_requests.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(sourcing_requests, 15)
    page_number = request.GET.get('page')
    requests_page = paginator.get_page(page_number)
    
    context = {
        'sourcing_requests': requests_page,
        'selected_status': status,
        'status_choices': SourcingRequest.STATUS_CHOICES,
    }
    return render(request, 'agent_module/sourcing_list.html', context)


@login_required
@agent_required
def sourcing_detail(request, request_id):
    """Sourcing request detail"""
    agent = request.user
    
    # Get sourcing request and verify
    sourcing_request = get_object_or_404(SourcingRequest, id=request_id)
    assignment = get_object_or_404(AgentAssignment, agent=agent, client=sourcing_request.user)
    
    quotes = sourcing_request.quotes.all()
    
    context = {
        'sourcing_request': sourcing_request,
        'quotes': quotes,
    }
    return render(request, 'agent_module/sourcing_detail.html', context)