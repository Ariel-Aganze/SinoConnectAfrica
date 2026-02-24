"""
Admin Module URL patterns
"""
from django.urls import path
from . import views

app_name = 'admin_module'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Order Management
    path('orders/', views.order_management, name='order_management'),
    path('orders/<uuid:order_id>/', views.order_detail_admin, name='order_detail_admin'),
    
    # Sourcing Management
    path('sourcing/', views.sourcing_management, name='sourcing_management'),
    path('sourcing/<uuid:request_id>/', views.sourcing_detail_admin, name='sourcing_detail_admin'),
    path('sourcing/<uuid:request_id>/create-quote/', views.create_quote, name='create_quote'),
    
    # Payment Verification
    path('payments/', views.payment_verification, name='payment_verification'),
    path('payments/<uuid:payment_id>/verify/', views.verify_payment, name='verify_payment'),
    
    # User Management
    path('users/', views.user_management, name='user_management'),
]