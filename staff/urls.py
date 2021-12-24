from django.urls import path

from . import views

app_name = 'staff'


urlpatterns = [
    path('', views.sales, name='staff_order_list')
]
