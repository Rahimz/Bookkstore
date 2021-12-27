from django.urls import path

from . import views
from .views import ProductCreate

app_name = 'staff'


urlpatterns = [
    path('orders/', views.orders, name='order_list'),
    path('orders/create/', views.order_create, name='order_create'),
    path('purchases/', views.purchases, name='purchase_list'),
    path('warehouse/', views.warehouse, name='warehouse'),
    path('products/', views.products, name='products'),
    path('products/create/', views.product_create, name='product_create'),

]
