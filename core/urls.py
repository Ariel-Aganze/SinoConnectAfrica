"""
Core URL patterns
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard redirect based on role
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    
    # Notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/<uuid:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Currency switcher
    path('set-currency/<str:currency_code>/', views.set_currency, name='set_currency'),
]