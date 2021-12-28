from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView

from . import views

app_name = 'shop'

urlpatterns = [
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('', views.temp_home, name='temp_home'),
    # path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('products/<slug:category_slug>/', views.product_list, name='products_list'),    
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]
