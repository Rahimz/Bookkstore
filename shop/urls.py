from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('product/123/', views.product_detail, name='product'),
    path('', views.temp_home, name='temp_home'),
    # path('', views.home, name='home'),
    path('home/', views.home, name='home'),
]
