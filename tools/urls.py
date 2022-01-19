from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [
    path('pdf/<int:order_id>/', views.make_invoice_pdf, name="make_invoice_pdf")
]
