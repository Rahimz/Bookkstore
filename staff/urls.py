from django.urls import path

from . import views
from .views import ProductCreate

app_name = 'staff'


urlpatterns = [
    path('sales/', views.sales, name='sales_list'),
    path('orders/<int:pk>/', views.order_detail_for_admin, name='order_detail_for_admin'),
    path('orders/shipping/<int:order_id>/', views.order_shipping, name='order_shipped'),
    # path('orders/sipping/<int:order_id>/', views.order_shipping, name='order_shipping'),
    path('orders/drafts/', views.draft_orders, name='draft_orders'),
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<str:period>/<str:channel>/', views.orders, name='order_list'),

    path('sales/countries/', views.order_list_by_country, name='order_list_by_country'),
    path('sales/countries/<str:country_code>/', views.order_list_by_country, name='order_list_by_country'),


    path('invoice/create/', views.invoice_create, name='invoice_create'),
    path('invoice/create/<int:order_id>/', views.invoice_create, name='invoice_create'),
    path('invoice/create/<int:order_id>/<int:book_id>/', views.invoice_create, name='invoice_add_book'),
    path('invoice/create/<int:order_id>/<int:book_id>/<str:variation>/', views.invoice_create, name='invoice_add_book_v'),

    path('invoice/create/new_order/<int:book_id>/', views.invoice_create, name='invoice_new_add_book'),
    path('invoice/create/new_order/<int:book_id>/<str:variation>/', views.invoice_create, name='invoice_new_add_book_v'),

    path('invoice/create/line-update/<int:order_id>/<int:orderline_id>/', views.orderline_update, name='orderline_update'),
    path('invoice/checkout/<int:order_id>/', views.invoice_checkout, name='invoice_checkout'),
    path('invoice/checkout/<int:order_id>/<int:client_id>/', views.invoice_checkout, name='invoice_checkout_client'),

    path('warehouse/', views.warehouse, name='warehouse'),
    path('warehouse/sold-products/', views.sold_products, name='sold_products'),
    path('warehouse/purchased-products/', views.purchased_products, name='purchased_products'),

    path('products/', views.products, name='products'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/update/<int:product_id>/', views.product_update, name='product_update'),

    path('categories/', views.category_list, name='categories'),
    path('category/create/', views.category_create, name='category_create'),

    path('vendor/list/', views.vendor_list, name='vendor_list'),
    path('vendor/add/', views.vendor_add, name='vendor_add'),
    path('vendor/edit/<int:vendor_id>/', views.vendor_edit, name='vendor_edit'),
]
