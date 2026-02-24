"""
Client Module URL patterns
"""
from django.urls import path
from . import views

app_name = 'client_module'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<uuid:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<uuid:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<uuid:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    
    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('orders/<uuid:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<uuid:order_id>/payment/', views.upload_payment_proof, name='upload_payment_proof'),
    
    # Sourcing
    path('sourcing/', views.sourcing_request_list, name='sourcing_request_list'),
    path('sourcing/new/', views.sourcing_request_create, name='sourcing_request_create'),
    path('sourcing/<uuid:request_id>/', views.sourcing_request_detail, name='sourcing_request_detail'),
    path('quotes/<uuid:quote_id>/accept/', views.accept_quote, name='accept_quote'),
    
    # Agent
    path('my-agent/', views.my_agent, name='my_agent'),
]