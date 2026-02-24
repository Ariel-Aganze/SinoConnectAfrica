"""
Core views for authentication and public pages
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import User, Product, Category, Notification, Currency, AgentAssignment
# from .forms import LoginForm, RegisterForm, ContactForm
from django import forms
from django.contrib.auth.forms import UserCreationForm



def home(request):
    """Homepage view"""
    featured_products = Product.objects.filter(is_active=True, featured=True)[:4]
    categories = Category.objects.filter(is_active=True)[:8]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'core/home.html', context)


def product_list(request):
    """Product listing page with filters"""
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    
    # Filters
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q')
    stock_status = request.GET.get('status')
    
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    if stock_status:
        products = products.filter(stock_status=stock_status)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)
    
    context = {
        'products': products_page,
        'categories': categories,
        'selected_category': category_slug,
        'search_query': search_query,
        'stock_status': stock_status,
    }
    return render(request, 'core/product_list.html', context)


def product_detail(request, slug):
    """Product detail page"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'core/product_detail.html', context)


def about(request):
    """About page"""
    return render(request, 'core/about.html')


def contact(request):
    """Contact page"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # TODO: Send email or save contact request
            messages.success(request, 'Votre message a été envoyé avec succès!')
            return redirect('core:contact')
    else:
        form = ContactForm()
    
    return render(request, 'core/contact.html', {'form': form})


class LoginForm(forms.Form):
    """Login form"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': 'votre@email.com'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': '••••••••'
        })
    )


class RegisterForm(UserCreationForm):
    """Registration form"""
    full_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': 'Nom complet'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': 'votre@email.com'
        })
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': 'Brazzaville, Pointe-Noire, Kinshasa...'
        })
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': '+242...'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': '••••••••'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': '••••••••'
        })
    )
    
    class Meta:
        model = User
        fields = ['full_name', 'email', 'city', 'phone_number', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.role = 'CLIENT'
        if commit:
            user.save()
        return user



class ContactForm(forms.Form):
    """Contact form"""
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': 'Votre nom'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': 'votre@email.com'
        })
    )
    subject = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': 'Sujet'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full bg-light border border-gray-200 text-gray-800 rounded-xl p-3.5 text-sm outline-none focus:border-action transition',
            'placeholder': 'Votre message...',
            'rows': 5
        })
    )


def login_view(request):
    """Login view"""
    if request.user.is_authenticated:
        return redirect('core:dashboard_redirect')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Try to authenticate with email as username
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue {user.full_name}!')
                
                # Redirect based on role
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('core:dashboard_redirect')
            else:
                messages.error(request, 'Email ou mot de passe incorrect.')
    else:
        form = LoginForm()
    
    return render(request, 'core/login.html', {'form': form})


def register_view(request):
    """Registration view"""
    if request.user.is_authenticated:
        return redirect('core:dashboard_redirect')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email  # Use email as username
            user.role = 'CLIENT'  # New users are clients by default
            user.save()
            
            # Auto-assign agent based on city
            assign_agent_to_client(user)
            
            # Login user automatically
            login(request, user)
            
            messages.success(request, 'Compte créé avec succès! Bienvenue sur SinoConnect Africa.')
            return redirect('core:dashboard_redirect')
    else:
        form = RegisterForm()
    
    return render(request, 'core/register.html', {'form': form})


@login_required
def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('core:home')


@login_required
def dashboard_redirect(request):
    """Redirect to appropriate dashboard based on user role"""
    if request.user.is_admin():
        return redirect('admin_module:dashboard')
    elif request.user.is_agent():
        return redirect('agent_module:dashboard')
    else:  # Client
        return redirect('client_module:dashboard')


@login_required
def notifications_list(request):
    """List all notifications for current user"""
    notifications = request.user.notifications.all()
    
    # Mark all as read if requested
    if request.GET.get('mark_all_read'):
        notifications.update(read=True)
        messages.success(request, 'Toutes les notifications ont été marquées comme lues.')
        return redirect('core:notifications_list')
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    notifications_page = paginator.get_page(page_number)
    
    context = {
        'notifications': notifications_page,
    }
    return render(request, 'core/notifications_list.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    
    # Redirect to link if provided
    if notification.link:
        return redirect(notification.link)
    
    return redirect('core:notifications_list')


def set_currency(request, currency_code):
    """Set user's preferred currency"""
    currency = get_object_or_404(Currency, code=currency_code, is_active=True)
    request.session['currency'] = currency_code
    
    # Redirect back to previous page
    next_url = request.GET.get('next', 'core:home')
    return redirect(next_url)


# Helper functions

def assign_agent_to_client(client):
    """Auto-assign agent to client based on city"""
    if not client.city:
        return
    
    # Find an agent in the same city
    agent = User.objects.filter(
        role='AGENT',
        city__iexact=client.city,
        is_active=True
    ).first()
    
    if agent:
        AgentAssignment.objects.create(
            client=client,
            agent=agent
        )
        
        # Create notification for client
        Notification.objects.create(
            user=client,
            type='SYSTEM',
            title='Agent assigné',
            message=f'{agent.full_name} a été assigné comme votre agent local à {client.city}.',
            link=None
        )