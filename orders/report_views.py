from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from math import trunc
from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum

from tools.gregory_to_hijry import hij_strf_date, greg_to_hij_date

from .models import Order, OrderLine, Purchase, PurchaseLine
from .forms import OrderCreateForm, PurchaseCreateForm, PurchaseLineAddForm, PriceAddForm, PurchaseLineUpdateForm
from cart.cart import Cart
from discounts.forms import CouponApplyForm
from search.forms import SearchForm
from search.views import ProductSearch
from products.models import Product
from products.price_management import add_price, has_empty_price_row, get_price_index, sort_price
from tools.fa_to_en_num import number_converter
from zarinpal.models import Payment


@staff_member_required
def sales_by_days(request, days=365, date=None):
    fa_date = None
    orders_approved_date = None
    orders_draft_date = None
    orders_all_date = None

    orders_book_date = None
    orders_craft_date = None
    orderline_all_date = None
    # print(date)
    if date:
        date = datetime.strptime(date, "%d%m%Y").date()
        fa_date = hij_strf_date(greg_to_hij_date(date), '%-d %B %Y')

    # print(fa_date)
    # hij_strf_date(greg_to_hij_date(order.created.date()), '%-d %B %Y')
        orders_all_date = Order.objects.filter(active=True).filter(created__date=date).aggregate(total=Sum('payable'), total_quantity=Sum('quantity'))
        orders_approved_date = Order.objects.filter(active=True).filter(status='approved').filter(created__date=date).aggregate(total=Sum('payable'), total_quantity=Sum('quantity'))
        orders_draft_date = Order.objects.filter(active=True).filter(status='draft').filter(created__date=date).aggregate(total=Sum('payable'), total_quantity=Sum('quantity'))

        orders_book_date = OrderLine.objects.filter(active=True).filter(created__date=date).exclude(product__product_type='craft').aggregate(total=Sum('cost_after_discount'), total_quantity=Sum('quantity'))
        orders_craft_date = OrderLine.objects.filter(active=True).filter(created__date=date).filter(product__product_type='craft').aggregate(total=Sum('cost_after_discount'), total_quantity=Sum('quantity'))
        orderline_all_date = OrderLine.objects.filter(active=True).filter(created__date=date).aggregate(total=Sum('cost_after_discount'), total_quantity=Sum('quantity'))


    orders_book = OrderLine.objects.filter(active=True).exclude(product__product_type='craft').aggregate(total=Sum('cost_after_discount'), total_quantity=Sum('quantity'))
    orders_craft = OrderLine.objects.filter(active=True).filter(product__product_type='craft').aggregate(total=Sum('cost_after_discount'), total_quantity=Sum('quantity'))
    orderline_all = OrderLine.objects.filter(active=True).aggregate(total=Sum('cost_after_discount'), total_quantity=Sum('quantity'))


    # dates_list = ['20022022', '21022022', '22022022']
    # the sales_date_dict structure
    # sales_date_dict = {
    #     '20022022': queryset <total_sales, orders_approved_date.total_quantity,>
    # }
    # sales_date_dict = {}
    # for item in dates_list:
    #     date = datetime.strptime(item, "%d%m%Y").date()
    #     sales_date_dict[item] = {
    #         'queryset': Order.objects.filter(active=True).filter(status='approved').filter(created__date=date).aggregate(total_approved=Sum('payable'), total_quantity=Sum('quantity'))
    #         }
    # order_lines = OrderLine.objects.all().filter(active=True).filter(created__date=date)
    # point = datetime.datetime.strptime('2022 3 5 16 11 26', "%Y %m %d %H %M %S")

    # order_lines = OrderLine.objects.all().filter(active=True).filter(created__gte=datetime.now() - timedelta(days)).exclude(product__product_type='craft').order_by('-created')
    order_0_day = Order.objects.filter(active=True).filter(created__date=(datetime.now().date())).aggregate(total_sales=Sum('payable'), total_quantity=Sum('quantity'))
    order_1_day = Order.objects.filter(active=True).filter(created__date=(datetime.now().date() - timedelta(days=1))).aggregate(total_sales=Sum('payable'), total_quantity=Sum('quantity'))
    order_2_day = Order.objects.filter(active=True).filter(created__date=(datetime.now().date()- timedelta(days=2))).aggregate(total_sales=Sum('payable'), total_quantity=Sum('quantity'))
    order_3_day = Order.objects.filter(active=True).filter(created__date=(datetime.now().date()- timedelta(days=3))).aggregate(total_sales=Sum('payable'), total_quantity=Sum('quantity'))
    order_4_day = Order.objects.filter(active=True).filter(created__date=(datetime.now().date()- timedelta(days=4))).aggregate(total_sales=Sum('payable'), total_quantity=Sum('quantity'))
    order_5_day = Order.objects.filter(active=True).filter(created__date=(datetime.now().date()- timedelta(days=5))).aggregate(total_sales=Sum('payable'), total_quantity=Sum('quantity'))
    order_6_day = Order.objects.filter(active=True).filter(created__date=(datetime.now().date()- timedelta(days=6))).aggregate(total_sales=Sum('payable'), total_quantity=Sum('quantity'))
    order_7_day = Order.objects.filter(active=True).filter(created__date=(datetime.now().date()- timedelta(days=7))).aggregate(total_sales=Sum('payable'), total_quantity=Sum('quantity'))
    order_8_day = Order.objects.filter(active=True).filter(created__date=(datetime.now().date()- timedelta(days=8))).aggregate(total_sales=Sum('payable'), total_quantity=Sum('quantity'))
    order_9_day = Order.objects.filter(active=True).filter(created__date=(datetime.now().date()- timedelta(days=9))).aggregate(total_sales=Sum('payable'), total_quantity=Sum('quantity'))



    order_approved = Order.objects.filter(active=True).filter(status='approved').aggregate(total_sales=Sum('payable'), total_quantity=Sum('quantity'))
    order_draft = Order.objects.filter(active=True).filter(status='draft').aggregate(total_sales=Sum('payable'), total_quantity=Sum('quantity'))
    order_all = Order.objects.filter(active=True).aggregate(total_sales=Sum('payable'), total_quantity=Sum('quantity'))


    all_payment = Payment.objects.filter(created__date__gte='2022-02-01').aggregate(total_amount=Sum('amount'))
    paid = Payment.objects.filter(created__date__gte='2022-02-01').filter(paid=True).aggregate(total_amount=Sum('amount'))
    pended = Payment.objects.filter(created__date__gte='2022-02-01').filter(paid=False).aggregate(total_amount=Sum('amount'))

    # report = {
    #     'sum':
    # }
    return render (
        request,
        'orders/reports/sales_by_days.html',
        {
            'order_approved': order_approved,
            'order_draft': order_draft,
            'order_all': order_all,
            # 'order_0_day': order_0_day,
            # 'order_1_day': order_1_day,
            # 'order_2_day': order_2_day,
            # 'order_3_day': order_3_day,
            # 'order_4_day': order_4_day,
            # 'order_5_day': order_5_day,
            # 'order_6_day': order_6_day,
            # 'order_7_day': order_7_day,
            # 'order_8_day': order_8_day,
            # 'order_9_day': order_9_day,
            'all_payment': all_payment,
            'paid': paid,
            'pended': pended,
            'orders_all_date': orders_all_date,
            'orders_approved_date': orders_approved_date,
            'orders_draft_date': orders_draft_date,
            'fa_date': fa_date,
            'orders_book_date': orders_book_date,
            'orders_craft_date': orders_craft_date,
            'orderline_all_date': orderline_all_date,
            'orders_book': orders_book , 
            'orders_craft': orders_craft,
            'orderline_all': orderline_all,
        }
    )
