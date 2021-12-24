from django.urls import path

from . import views

app_name = 'staff'


urlpatterns = [
    path('orders/', views.orders, name='order_list'),
    path('purchases/', views.purchases, name='purchase_list'),
    path('warehouse/', views.warehouse, name='warehouse'),

]
