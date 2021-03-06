from django.urls import path

from . import views
from .views import ProductCreate
from warehouses.views import refund_from_client, refund_list_client

app_name = 'staff'


urlpatterns = [
    # path('sales/', views.sales, name='sales_list'),
    path('orders/details/<int:pk>/', views.order_detail_for_admin, name='order_detail_for_admin'),
    path('orders/shipping/<int:order_id>/', views.order_shipping, name='order_shipped'),

    path('orders/full-shipped-list/', views.full_shipped_list, name='full_shipped_list'),
    path('orders/full-shipped-list/<str:date>/', views.full_shipped_list, name='full_shipped_list_date'),
    # path('orders/sipping/<int:order_id>/', views.order_shipping, name='order_shipping'),
    path('orders/drafts/', views.draft_orders, name='draft_orders'),
    path('orders/remove-draft/<int:order_id>/', views.remove_draft_order, name='remove_draft_order'),

    path('orders/create/', views.order_create, name='order_create'),
    # path('orders/', views.orders, name='order_list'),
    # path('orders/<str:channel>/', views.orders, name='order_list_by_channel'),
    # path('orders/<str:channel>/<str:period>/', views.orders, name='order_list_by_channel_period'),
    path('orders/<str:channel>/<str:period>/', views.orders, name='order_list'),
    path('orders/<str:channel>/<str:period>/<str:filter>/', views.orders, name='order_list_filter'),

    path('sales/countries/', views.order_list_by_country, name='order_list_by_country'),
    path('sales/countries/<str:country_code>/', views.order_list_by_country, name='order_list_by_country'),

    path('sales/vendor/', views.sales_by_vendor, name='sales_by_vendor'),
    path('sales/vendor/<int:vendor_id>/<str:date>/', views.sales_by_vendor, name='sales_by_vendor'),


    path('invoice/create/', views.invoice_create, name='invoice_create'),
    path('invoice/create/<int:order_id>/', views.invoice_create, name='invoice_create'),
    path('invoice/create/<int:order_id>/<int:book_id>/', views.invoice_create, name='invoice_add_book'),
    path('invoice/create/<int:order_id>/<int:book_id>/<str:variation>/', views.invoice_create, name='invoice_add_book_v'),

    path('invoice/create/new_order/<int:book_id>/', views.invoice_create, name='invoice_new_add_book'),
    path('invoice/create/new_order/<int:book_id>/<str:variation>/', views.invoice_create, name='invoice_new_add_book_v'),

    path('invoice/create/<int:order_id>/add-client/', views.invoice_create_add_client, name='invoice_add_client'),
    path('invoice/create/<int:order_id>/add-client/<int:client_id>/', views.invoice_create_add_client, name='invoice_add_client_ok'),
    path('invoice/remove-client/<int:order_id>/', views.remove_client_from_order, name='remove_client_from_order'),

    path('invoice/create/line-update/<int:order_id>/<int:orderline_id>/', views.orderline_update, name='orderline_update'),
    path('invoice/checkout/<int:order_id>/', views.invoice_checkout, name='invoice_checkout'),
    path('invoice/checkout/<int:order_id>/<int:client_id>/', views.invoice_checkout, name='invoice_checkout_client'),
    path('invoice/checkout/credit-pay/<int:order_id>/<int:client_id>/', views.invoice_checkout_credit, name='invoice_checkout_client_credit'),
    path('invoice/checkout/credit-remove/<int:order_id>/', views.invoice_remove_credit, name='invoice_remove_credit'),

    path('invoice/back-to-draft/<int:order_id>/', views.invoice_back_to_draft, name='invoice_back_to_draft'),
    path('invoice/payment-manage/<int:order_id>/', views.order_payment_manage, name='order_payment_manage'),

    path('warehouse/', views.warehouse, name='warehouse'),
    path('warehouse/sold-products/<int:days>/', views.sold_products, name='sold_products'),
    path('warehouse/sold-products/date/<str:date>/', views.sold_products, name='sold_products_date'),
    path('warehouse/sold-products/period/<str:period>/', views.sold_products, name='sold_products_date_period'),

    path('warehouse/purchased-products/', views.purchased_products, name='purchased_products'),
    path('warehouse/refund/client/', refund_from_client, name="refund_from_client"),
    path('warehouse/refund/client/list/', refund_list_client, name="refund_list_client"),

    path('warehouse/zero-stock-list/', views.zero_stock_list, name="zero_stock_list"),

    path('products/', views.products, name='products'),
    path('products/create/', views.product_create, name='product_create'),
    # path('products/update/<int:product_id>/', views.product_update, name='product_update'),
    path('products/update/<int:product_id>/', views.product_create, name='product_update'),
    path('products/image-management/<int:product_id>/', views.image_management, name='image_management'),
    path('products/image-remove/<int:image_id>/<int:product_id>/', views.image_remove, name='image_remove'),
    path('products/price-show/<int:product_id>/', views.product_price_show, name='product_price_show'),

    path('products/collection-management/', views.collection_management, name='collection_management'),
    path('products/collection-management/edit/<int:product_id>/', views.collection_management_edit, name='collection_management_edit'),
    path('products/collection-management/edit/<int:product_id>/<str:product_isbn>/', views.collection_management_remove, name='collection_management_remove'),

    path('products/reports/', views.product_reports, name='product_reports'),

    path('categories/', views.category_list, name='categories'),
    path('category/create/', views.category_create, name='category_create'),

    path('vendor/list/', views.vendor_list, name='vendor_list'),
    path('vendor/add/', views.vendor_add, name='vendor_add'),
    path('vendor/edit/<int:vendor_id>/', views.vendor_edit, name='vendor_edit'),

    path('products/used-book/price-management/<int:product_id>/', views.used_book_prices, name="used_book_prices"),
    path('products/price-stock-management/<int:product_id>/', views.product_stock_price_edit, name="product_stock_price_edit"),

    path('products/crafts/', views.craft_list, name="craft_list"),
    path('products/crafts-update/<int:craft_id>/', views.craft_update, name="craft_update"),
    path('products/crafts-create/', views.craft_update, name="craft_create"),
]
