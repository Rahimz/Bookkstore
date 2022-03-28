from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [
    path('pdf/<int:order_id>/', views.make_invoice_pdf, name="make_invoice_pdf"),
    path('pdf/<int:order_id>/print/', views.print_invoice, name="print_invoice"),
    path('pdf/a4/<int:order_id>/', views.make_invoice_pdf_a4, name="make_invoice_pdf_a4"),

    path('print/address/<int:client_id>/<str:kind>/', views.print_address, name="print_address"),

    path('order-export/<str:criteria>/', views.order_export_excel, name="order_export_excel"),
    path('order-export/<str:criteria>/<str:date>/', views.order_export_excel, name="order_export_excel_date"),

    path('draft-order-export/', views.draft_order_export_excel, name="draft_order_export_excel"),
    path('publishers-export/', views.export_publisher, name="export_publisher"),

    path('product-export/', views.product_export_excel, name="product_export_excel"),
    path('used-product-without-price-export/<str:filter>/', views.product_export_excel, name="used_noprice_export_excel"),
    path('used-product-all-export/<str:filter>/', views.product_export_excel, name="used_all_export_excel"),

    path('used-product-before-5/', views.used_product_before_5, name="used_product_before_5"),

    path('qrcode/create/<int:order_id>/<int:payment_id>/', views.qrcode_create, name='qrcode_create'),

    path('export-sold-products/<int:days>/', views.export_excel_sold_products, name="export_excel_sold_products"),
    path('export-sold-products/date/<str:date>/', views.export_excel_sold_products, name="export_excel_sold_products_date"),

    path('duplicate-book-name/', views.duplicate_book_name, name="duplicate_book_name"),
    path('duplicate-book-name/export', views.duplicate_book_name_export, name="duplicate_book_name_export"),
]
