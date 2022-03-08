from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
import calendar
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

    orders_paid_date = None
    orders_unpaid_date = None

    year = '2022'
    month = '03'
    num_days = calendar.monthrange(2022, 3)[1]

    # date_list is dictionary with day in persian and greg date in string
    # dates_list = {
    #     '02': [('12', '20220201'), ('13', '20220202'), ('14', '20220203'), ...],
    #     '03': [('10', '20220301'), ('11', '20220302'), ('12', '20220303'), ...],
    # }
    dates_list = {}

    month_code = ['02', '03',]
    for month in month_code:
        num_days = calendar.monthrange(2022, int(month))[1]
        dates_list[month] = list()
        for day in range(1, num_days+1):
            date_string = f"{year}{month}{'0'+str(day) if day<10 else str(day)}"
            date_obj = datetime.strptime(date_string, "%Y%m%d").date()
            fa_date_day = hij_strf_date(greg_to_hij_date(date_obj), '%-d')
            dates_list[month].append((fa_date_day, date_string))
    # # TODO: We want to make a list of (fa_day, greg_date) to make report
    # fa_date_list = {'12': []}
    # for item in dates_list:
    #     if int(dates_list[item][1]) > int('20220220'):
    #         fa_date_list['12'].append(ates_list[item])
    # print(fa_dates_list)

    # print(date)
    if date:
        date = datetime.strptime(date, "%d%m%Y").date()
        fa_date = hij_strf_date(greg_to_hij_date(date), '%-d %B %Y')

    # print(fa_date)
    # hij_strf_date(greg_to_hij_date(order.created.date()), '%-d %B %Y')
        orders_all_date = Order.objects.filter(active=True).filter(created__date=date).aggregate(total=Sum('payable'), total_quantity=Sum('quantity'))
        orders_approved_date = Order.objects.filter(active=True).filter(status='approved').filter(created__date=date).aggregate(total=Sum('payable'), total_quantity=Sum('quantity'))
        orders_draft_date = Order.objects.filter(active=True).filter(status='draft').filter(created__date=date).aggregate(total=Sum('payable'), total_quantity=Sum('quantity'))

        orders_paid_date = Order.objects.filter(active=True).filter(paid=True).filter(created__date=date).aggregate(total=Sum('payable'), total_quantity=Sum('quantity'))
        orders_unpaid_date = Order.objects.filter(active=True).filter(paid=False).filter(created__date=date).aggregate(total=Sum('payable'), total_quantity=Sum('quantity'))

        orders_book_date = OrderLine.objects.filter(active=True).filter(created__date=date).exclude(product__product_type='craft').aggregate(total=Sum('cost_after_discount'), total_quantity=Sum('quantity'))
        orders_craft_date = OrderLine.objects.filter(active=True).filter(created__date=date).filter(product__product_type='craft').aggregate(total=Sum('cost_after_discount'), total_quantity=Sum('quantity'))
        orderline_all_date = OrderLine.objects.filter(active=True).filter(created__date=date).aggregate(total=Sum('cost_after_discount'), total_quantity=Sum('quantity'))


    orders_book = OrderLine.objects.filter(active=True).exclude(product__product_type='craft').aggregate(total=Sum('cost_after_discount'), total_quantity=Sum('quantity'))
    orders_craft = OrderLine.objects.filter(active=True).filter(product__product_type='craft').aggregate(total=Sum('cost_after_discount'), total_quantity=Sum('quantity'))
    orderline_all = OrderLine.objects.filter(active=True).aggregate(total=Sum('cost_after_discount'), total_quantity=Sum('quantity'))

    orders_paid_all = Order.objects.filter(active=True).filter(paid=True).aggregate(total=Sum('payable'), total_quantity=Sum('quantity'))
    orders_unpaid_all = Order.objects.filter(active=True).filter(paid=False).aggregate(total=Sum('payable'), total_quantity=Sum('quantity'))

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




    order_approved = Order.objects.filter(active=True).filter(status='approved').aggregate(total_sales=Sum('payable'), total_quantity=Sum('quantity'))
    order_draft = Order.objects.filter(active=True).filter(status='draft').aggregate(total_sales=Sum('payable'), total_quantity=Sum('quantity'))
    order_all = Order.objects.filter(active=True).aggregate(total_sales=Sum('payable'), total_quantity=Sum('quantity'))


    all_payment = Payment.objects.filter(created__date__gte='2022-02-01').aggregate(total_amount=Sum('amount'))
    paid = Payment.objects.filter(created__date__gte='2022-02-01').filter(paid=True).aggregate(total_amount=Sum('amount'))
    pended = Payment.objects.filter(created__date__gte='2022-02-01').filter(paid=False).aggregate(total_amount=Sum('amount'))


    return render (
        request,
        'orders/reports/sales_by_days.html',
        {
            'order_approved': order_approved,
            'order_draft': order_draft,
            'order_all': order_all,
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
            'orders_paid_date': orders_paid_date,
            'orders_unpaid_date': orders_unpaid_date,
            'orders_paid_all': orders_paid_all,
            'orders_unpaid_all': orders_unpaid_all,
        }
    )
