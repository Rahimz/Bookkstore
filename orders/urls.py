from django.urls import path
from . import views


app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),

    path('purchase/create/', views.purchase_create, name='purchase_create'),
    path('purchase/list/', views.purchase_list, name='purchase_list'),
    path('purchase/<int:purchase_id>/', views.purchase_details, name='purchase_details'),
    path('purchase/edit/<int:purchase_id>/', views.purchase_update, name='purchase_update'),
]
