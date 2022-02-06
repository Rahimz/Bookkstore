from django.urls import path
from . import views


app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),

    path('purchase/create/', views.purchase_create, name='purchase_create'),
    path('purchase/list/', views.purchase_list, name='purchase_list'),
]
