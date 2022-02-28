from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from math import trunc
from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum


from .models import Order, OrderLine, Purchase, PurchaseLine
from .forms import OrderCreateForm, PurchaseCreateForm, PurchaseLineAddForm, PriceAddForm, PurchaseLineUpdateForm
from cart.cart import Cart
from discounts.forms import CouponApplyForm
from search.forms import SearchForm
from search.views import ProductSearch
from products.models import Product
from products.price_management import add_price, has_empty_price_row, get_price_index, sort_price
from tools.fa_to_en_num import number_converter


@staff_member_required
def sales_by_days(request, days=365):
    print(datetime.now().date()- timedelta(days=1))
    print(datetime.now().date()- timedelta(days=2))
    print(datetime.now().date()- timedelta(days=3))
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
            'order_0_day': order_0_day,
            'order_1_day': order_1_day,
            'order_2_day': order_2_day,
            'order_3_day': order_3_day,
            'order_4_day': order_4_day,
            'order_5_day': order_5_day,
            'order_6_day': order_6_day,
            'order_7_day': order_7_day,
            'order_8_day': order_8_day,
            'order_9_day': order_9_day,
        }
    )
