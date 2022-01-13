from django.urls import path
from . import views


app_name = 'zarinpal'

urlpatterns = [
    path('request/', views.send_request, name='request'),
    path('verify/', views.verify , name='verify'),
    path('form_verify/', views.form_verify , name='form_verify'),
    path('payment-form/', views.form_payment , name='form_payment'),
]
