from django.urls import path
from . import views
from . import report_views


app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),

    path('purchase/create/', views.purchase_create, name='purchase_create'),
    path('purchase/list/', views.purchase_list, name='purchase_list'),
    path('purchase/edit/<int:purchase_id>/', views.purchase_update, name='purchase_update'), # for updating main purchase model

    path('purchase/<int:purchase_id>/', views.purchase_details, name='purchase_details'),
    # path('purchase/<int:purchase_id>/add/<int:product_id>/', views.purchase_details, name='purchase_add_line'),
    path('purchase/add-line/<int:purchase_id>/<int:product_id>/<str:variation>/', views.purchase_line_add, name='purchaseline_add'),
    path('purchase/add-line/<int:purchase_id>/<int:product_id>/<str:variation>/<int:purchaseline_id>/', views.purchase_line_add, name='purchaseline_update'),
    path('purchaseline/remove/<int:purchaseline_id>/', views.purchaseline_remove, name='purchaseline_remove'),

    path('purchase/<int:purchase_id>/add/<int:product_id>/<str:variation>/', views.purchase_details, name='purchase_add_line_v'),

    path('purchase/price-management/<int:purchase_id>/<int:product_id>/', views.price_management, name='price_management'),
    path('purchase/price-management/remove-price/<int:purchase_id>/<int:product_id>/<str:variation>/', views.price_remove, name='price_remove'),

    path('purchase/checkout/<int:purchase_id>/', views.purchase_checkout, name='purchase_checkout'),

    path('report/sales-by-days/<int:days>/', report_views.sales_by_days, name='sales_by_days'),
]
