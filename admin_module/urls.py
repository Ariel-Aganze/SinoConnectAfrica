from django.urls import path
from . import views

app_name = 'admin_module'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Orders
    path('orders/', views.order_management, name='order_management'),
    path('orders/<uuid:order_id>/', views.order_detail_admin, name='order_detail_admin'),
    
    # Payments
    path('payments/', views.payment_verification, name='payment_verification'),
    path('payments/<uuid:payment_id>/verify/', views.verify_payment, name='verify_payment'),
    
    # Sourcing
    path('sourcing/', views.sourcing_management, name='sourcing_management'),
    path('sourcing/<uuid:request_id>/', views.sourcing_detail_admin, name='sourcing_detail_admin'),
    path('sourcing/<uuid:request_id>/create-quote/', views.create_quote, name='create_quote'),
    
    # Users
    path('users/', views.user_management, name='user_management'),
    path('users/<uuid:user_id>/', views.user_detail_admin, name='user_detail_admin'),
    
    # Products
    path('products/', views.product_management, name='product_management'),
    path('products/get/<uuid:product_id>/', views.get_product_data, name='get_product_data'),  # ← NOUVELLE ROUTE
    
    # Categories
    path('categories/', views.category_management, name='category_management'),
    path('categories/get/<uuid:category_id>/', views.get_category_data, name='get_category_data'), 
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
]