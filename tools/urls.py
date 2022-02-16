from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [
    path('pdf/<int:order_id>/', views.make_invoice_pdf, name="make_invoice_pdf"),
    path('pdf/<int:order_id>/print/', views.print_invoice, name="print_invoice"),
    path('pdf/a4/<int:order_id>/', views.make_invoice_pdf_a4, name="make_invoice_pdf_a4"),

    path('order-export/<str:criteria>/', views.order_export_excel, name="order_export_excel"),
    path('draft-order-export/', views.draft_order_export_excel, name="draft_order_export_excel"),
]
