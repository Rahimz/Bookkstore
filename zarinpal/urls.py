from django.urls import path
from . import views


app_name = 'zarinpal'

urlpatterns = [
    path('request/', views.send_request, name='request'),
    path('verify/', views.verify , name='verify'),
    path('form_verify/', views.form_verify , name='form_verify'),
    path('payment-form/', views.form_payment , name='form_payment'),
    path('payment/create/', views.payment_create , name='payment_create'),
    path('payment-link/<int:pay_id>/', views.send_form_request , name='payment_link_request'),
    path('payments/', views.payment_list , name='payment_list'),
    path('payments/already_paid/', views.already_paid , name='already_paid'),
]
