"""
Agent Module URL patterns
"""
from django.urls import path
from . import views

app_name = 'agent_module'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Clients
    path('clients/', views.client_list, name='client_list'),
    path('clients/<uuid:client_id>/', views.client_detail, name='client_detail'),
    
    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('orders/<uuid:order_id>/', views.order_detail, name='order_detail'),
    
    # Sourcing
    path('sourcing/', views.sourcing_list, name='sourcing_list'),
    path('sourcing/<uuid:request_id>/', views.sourcing_detail, name='sourcing_detail'),
]