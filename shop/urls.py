from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'shop'

urlpatterns = [
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('', views.temp_home, name='temp_home'),
    # path('', views.home, name='home'),
    path('home/', views.home, name='home'),
]
