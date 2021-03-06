from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.postgres.search import SearchVector
from django.db.models import Q, Count
import uuid
from datetime import datetime, timedelta
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum
from decimal import Decimal
from django.core.cache import cache
import random

from django_countries.fields import Country
from tools.gregory_to_hijry import hij_strf_date, greg_to_hij_date

from .forms import ProductCreateForm, OrderCreateForm, InvoiceAddForm, CategoryCreateForm, OrderShippingForm, ProductCollectionForm, AdminPriceManagementForm
from .forms import CraftUpdateForm, AdminPriceStockManagementForm, OnlineAdminPriceStockManagementForm, ProductImageManagementForm
from orders.forms import OrderAdminCheckoutForm, OrderPaymentManageForm
from search.forms import ClientSearchForm, BookIsbnSearchForm, SearchForm, OrderSearchForm
from account.forms import VendorAddForm, AddressAddForm, VendorAddressAddForm
from products.models import Product, Category, Image
from orders.models import Order, OrderLine, PurchaseLine, Purchase
from products.models import Craft
from account.models import CustomUser, Vendor, Address, Credit
from search.views import ProductSearch
from tools.fa_to_en_num import number_converter
from tools.gregory_to_hijry import *
from tools.views import notif_email_to_managers
from products.price_management import get_price_index


def sales(request):
    return render(
        request,
        'staff/sales.html',
        {}
    )


@staff_member_required
def orders(request, period='all', channel='all', filter=None):
    orders = Order.objects.filter(active=True).filter(status='approved')
    channel_list = [item[0] for item in Order.CHANNEL_CHOICES]

    today_date = datetime.now().date()
    today = today_date.strftime("%Y%m%d")

    last_1_day_date = today_date - timedelta(1)
    last_1_day = last_1_day_date.strftime("%Y%m%d")
    yesterday = f"{last_1_day}-{today}"

    last_7_day_date = today_date - timedelta(7)
    last_7_day = last_7_day_date.strftime("%Y%m%d")
    last_week = f"{last_7_day}-{today}"

    last_30_day_date = today_date - timedelta(30)
    last_30_day = last_30_day_date.strftime("%Y%m%d")
    last_month = f"{last_30_day}-{today}"

    if channel == 'collectable':
        orders = orders.exclude(channel='cashier')
    elif channel != 'all':
        orders = orders.filter(channel=channel)

    if period != 'all':
        # period should be like '20220320-20220322'
        period_list = list(period.split('-'))
        start_date = datetime.strptime(period_list[0], "%Y%m%d").date()
        end_date = datetime.strptime(period_list[1], "%Y%m%d").date()
        orders = orders.filter(created__date__gte=start_date, created__date__lte=end_date)

    if request.method == 'POST':
        search_form = OrderSearchForm(request.POST)
        if search_form.is_valid():
            query = search_form.cleaned_data['order_query']
            orders = orders.annotate(
                search=SearchVector(
                    'client__first_name', 'client__last_name', 'client__phone',
                    'pk', 'channel', 'shipping_time'
                ),).filter(search=query)
    else:
        search_form = OrderSearchForm()

    # filter
    if filter:
        orders = orders.order_by(filter)

    # order statics
    orders_statics = orders.aggregate(cost=Sum('payable'), quantity=Sum('quantity'))

    # we make a session variable to send order list to other needed veiw
    request.session['orders'] = list(orders.values_list('id', flat=True))

    # pagination
    paginator = Paginator(orders, 20)  # 20 order in each page
    page = request.GET.get('page')
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        orders = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        orders = paginator.page(paginator.num_pages)


    return render(
        request,
        'staff/orders.html',
        {
            'orders': orders,
            'search_form': search_form,
            'page': page,
            'period': period,
            'channel': channel,
            'yesterday': yesterday,
            'last_week': last_week,
            'last_month': last_month,
            'channel_list': channel_list,
            'orders_statics': orders_statics,
        }
    )


@staff_member_required
def order_detail_for_admin(request, pk):
    order = get_object_or_404(Order, pk=pk)

    # this part added for updating those orders that have not the client address in them
    client = order.client
    if client.username != 'guest':
        order.billing_address = client.default_billing_address
        order.shipping_address = client.default_shipping_address
    # print(order.billing_address.get_full_address())
    order.save()
    return render(
        request,
        'staff/order_detail_for_admin.html',
        {'order': order}
    )


@staff_member_required
def warehouse(request):
    return render(
        request,
        'staff/warehouse.html',
        {}
    )


@staff_member_required
def products(request):
    search_query = None
    page = None
    # This if statement check if we have a search result or not
    # if we dont have result then make a wuery set for products
    products = Product.objects.all().filter(
        available=True).exclude(product_type='craft')
    counts = products.count()

    search_form = SearchForm()
    if request.method == 'POST':
        search_form = SearchForm(data=request.POST)
        if search_form.is_valid():
            search_query = search_form.cleaned_data['query']
            search_query = number_converter(search_query)
            products = ProductSearch(
                object=Product, query=search_query).exclude(product_type='craft').order_by('name', 'publisher')
            counts = products.count()

            search_form = SearchForm()

    if not search_query:
        # becuase we have bugs in pagination and search together
        # we do not paginate the search results
        # pagination
        paginator = Paginator(products, 50)  # 50 posts in each page
        page = request.GET.get('page')
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer deliver the first page
            products = paginator.page(1)
        except EmptyPage:
            # If page is out of range deliver last page of results
            products = paginator.page(paginator.num_pages)

    return render(
        request,
        'staff/products.html',
        {
            'products': products,
            'page': page,
            'counts': counts,
            'search_form': search_form,
        }
    )


@staff_member_required
def product_create(request, product_id=None):
    if product_id:
        product = get_object_or_404(Product, pk=product_id)
    else:
        product = None
    if request.method == 'POST':
        if product:
            form = ProductCreateForm(
                data=request.POST,
                instance=product,
                files=request.FILES)
        else:
            form = ProductCreateForm(
                data=request.POST,
                files=request.FILES)
        if form.is_valid():
            new_product = form.save(commit=False)
            # # TODO: this part does not work properly
            # new_product.product_type = 'book'
            # if form.price_1 or form.price_2 or form.price_3 or form.price_4 or form.price_5 or form.price_used:
            #     new_product.has_other_prices = True
            # if form.stock_1 or form.stock_2 or form.stock_3 or form.stock_4 or form.stock_5 or form.stock_used:
            #     new_product.has_other_prices = True
            # if form.stock_used:
            #     new_product.has_other_prices = True
            # new_product.save()
            if not product:
                isbn = new_product.isbn if new_product.isbn else None
                if isbn:
                    if len(isbn) == 13:
                        isbn_9 = isbn[3:-1]
                    elif len(isbn) == 12:
                        isbn_9 = isbn[3:]
                    elif len(isbn) == 10:
                        isbn_9 = isbn[:-1]
                    elif len(isbn) == 9:
                        isbn_9 = isbn
                    else:
                        isbn_9 = None
                products = None
                try:
                    if isbn_9:
                        products = Product.objects.filter(
                            available=True).filter(isbn_9=isbn_9)
                    else:
                        products = Product.objects.filter(
                            available=True).filter(isbn=isbn)
                except:
                    pass
                if products:
                    if len(products) > 0:
                        if isbn_9:
                            product = Product.objects.get(isbn_9=isbn_9)
                        else:
                            product = Product.objects.get(isbn=isbn)
                        messages.error(request, _(
                            'A product with same isbn is available') + ': {} - {}'.format(product.name, product.isbn))
                        return redirect('staff:product_create')
            new_product.save()

            # Updating the publisher product count when any product updated or created
            publisher_1 = new_product.pub_1
            publisher_2 = new_product.pub_2
            if publisher_1:
                publisher_1.product_count = Product.objects.filter(available=True).filter( Q(pub_1=publisher_1) | Q(pub_2=publisher_1) ).exclude(product_type='craft').count()
                publisher_1.save()
            if publisher_2:
                publisher_2.product_count = Product.objects.filter(available=True).filter( Q(pub_1=publisher_2) | Q(pub_2=publisher_2) ).exclude(product_type='craft').count()
                publisher_2.save()

            if product_id:
                messages.success(request, _('Product updated'))
            else:
                messages.success(request, _('Product is created'))

            if 'another' in request.POST:
                return HttpResponseRedirect(reverse('staff:product_create'))
            return HttpResponseRedirect(reverse('staff:products'))

    else:
        if product:
            form = ProductCreateForm(instance=product)
        else:
            form = ProductCreateForm()
    return render(
        request,
        'staff/product_create.html',
        {'form': form}
    )


# @staff_member_required
# def product_update(request, product_id):
#     product = get_object_or_404(Product, pk=product_id)
#     if request.method == 'POST':
#         form = ProductCreateForm(
#             data=request.POST,
#             instance=product,
#             files=request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, _('Product updated') +
#                              ' {}'.format(product.name))
#             return redirect('staff:products')
#
#         else:
#             messages.error(request, _('Form is not valid'))
#     else:
#         form = ProductCreateForm(instance=product)
#
#     return render(
#         request,
#         'staff/product_create.html',
#         {'form': form}
#
#     )


@staff_member_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryCreateForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.save()
            messages.success(request, _('Category is created!'))
            if 'another' in request.POST:
                return HttpResponseRedirect(reverse('staff:category_create'))
            return HttpResponseRedirect(reverse('staff:products'))
        else:
            messages.error(request, _('Form is not valid'))
    else:
        form = CategoryCreateForm()
    return render(
        request,
        'staff/category_create.html',
        {'form': form}
    )


@staff_member_required
def order_create(request):
    form = OrderCreateForm()
    return render(
        request,
        'staff/order_create.html',
        {'form': form}
    )


@staff_member_required
class ProductCreate(View):
    # template = 'staff/product_create.html'

    def get(self, request):
        return reverse('staff:product_create')

    def post(self, request):
        if request.method == 'POST':
            form = ProductCreateForm()
            if form.is_valid:
                product = form.save(commit=False)
                product.save()
                messages.success(request, _('Product is created!'))
        if "cancel" in request.POST:
            return HttpResponseRedirect(reverse('staff:products'))
        return super(ProductCreate, self).post(request, *args, **kwargs)

    def get_success_url(self):
        if "another" in self.request.POST:
            return reverse('staff:product_create')
        # else return the default `success_url`
        return super(ProductCreate, self).get_success_url()

        if request.method == 'POST':
            form = ProductCreateForm()
            if form.is_valid():
                product = form.save()
                messages.success(request, _('Product created'))
                return HttpResponseRedirect(reverse('shop:home'))
            else:
                messages.error(request, _('Product does not created!'))
        else:
            form = ProductCreateForm()
        return render(
            request,
            'staff/product_create.html',
            {'form': form}
        )


@staff_member_required
def invoice_create(request, order_id=None, book_id=None, variation='new main'):
    product_id = book_id
    products = None
    results = None
    product = None
    # warnin for collection
    collection_warning = False
    collection_ids = []
    collection_parent_product = None
    collection_children_product = None
    # isbn = ''
    search_form = SearchForm()
    update_form = InvoiceAddForm()
    product_ids = []
    update_forms = {}

    if variation == 'main':
        variation = 'new main'
    elif variation == 'v1':
        variation = 'new v1'
    elif variation == 'used':
        variation = 'used main'
    variation_list = variation.split()
    # order_line.variation = variation
    # order_line.save()

    if order_id:
        order = get_object_or_404(Order, pk=order_id)
        product_ids = [(item.product.pk, item.variation)
                       for item in order.lines.all()]

        # TODO: The loop should be replaced with a query to enhance the performance
        for item in order.lines.all():
            if item.product.is_collection:
                collection_warning = True
                collection_ids.append(
                    (item.product.pk, item.product.collection_set, item.product.collection_parent))
            # update_forms[item.id]
            form = InvoiceAddForm()
            update_forms[item.id] = form

    else:
        order = None

    if product_id:
        product = Product.objects.get(pk=product_id)

        # in this dict we handle the other prices and quantities variations

        variation_dict = {
            'new': {
                'main': {
                    'price': product.price,
                    'stock': product.stock,
                },
                'v1': {
                    'price': product.price_1,
                    'stock': product.stock_1,
                },
                'v2': {
                    'price': product.price_2,
                    'stock': product.stock_2,
                },
                'v3': {
                    'price': product.price_3,
                    'stock': product.stock_3,
                },
                'v4': {
                    'price': product.price_4,
                    'stock': product.stock_4,
                },
                'v5': {
                    'price': product.price_5,
                    'stock': product.stock_5,
                },
            },
            'used': {
                'main': {
                    'price': product.price_used,
                    'stock': product.stock_used
                },
            }
        }

        price = variation_dict[variation_list[0]][variation_list[1]]['price']
        stock = variation_dict[variation_list[0]][variation_list[1]]['stock']
    isbn_search_form = BookIsbnSearchForm()

    # If the search result contains more than one results
    #  we handle it in these if statement
    if order_id and product_id:

        # Check the stock of product
        if price == 0:
            messages.error(request, _(
                'You could not add product without price'))
            return redirect('staff:invoice_create', order_id)

        if stock <= 0:
            messages.error(request, _('You are adding zero stock!'))
            # return redirect('staff:invoice_create', order_id)

        # add product to invoice
        if (product.id, variation) in product_ids:
            order_line = OrderLine.objects.get(
                order=order, product=product, variation=variation)
            order_line.quantity += 1
            order_line.save()
            order.save()
        else:
            order_line = OrderLine.objects.create(
                order=order,
                product=product,
                quantity=1,
                price=price,
                variation=variation,
                discount=0
            )
            order.save()

        # Update product stock
        stock -= 1

        if variation == 'new main':
            product.stock = stock

        elif variation == 'new v1':
            product.stock_1 = stock

        elif variation == 'new v2':
            product.stock_2 = stock

        elif variation == 'new v3':
            product.stock_3 = stock

        elif variation == 'new v3':
            product.stock_4 = stock

        elif variation == 'new v4':
            product.stock_5 = stock

        elif variation == 'used main':
            product.stock_used = stock
        product.save()

        messages.success(request, _('Product is added to invoice'))

        return redirect('staff:invoice_create', order.id)

    # When we add a product for first time and we dont have an order
    if (not order_id) and product_id:
        if price == 0:
            messages.error(request, _(
                'You could not add product without price'))
            return redirect('staff:invoice_create')

        if stock <= 0:
            messages.error(request, _('You are adding zero stock!'))
            # return redirect('staff:invoice_create')

        # if product.stock >=1:
        order = Order.objects.create(
            user=request.user,
            status='draft',
            shipping_method='pickup',
        )
        messages.success(request, _('Order is created') +
                         ' : {}'.format(order.id))
        order_line = OrderLine.objects.create(
            order=order,
            product=product,
            quantity=1,
            price=price,
            variation=variation,
            discount=0
        )
        order.save()

        # Update product stock
        stock -= 1

        if variation == 'new main':
            product.stock = stock

        elif variation == 'new v1':
            product.stock_1 = stock

        elif variation == 'new v2':
            product.stock_2 = stock

        elif variation == 'new v3':
            product.stock_3 = stock

        elif variation == 'new v3':
            product.stock_4 = stock

        elif variation == 'new v4':
            product.stock_5 = stock

        elif variation == 'used main':
            product.stock_used = stock

        product.save()

        messages.success(request,  _('Product is added to invoice'))
        return redirect('staff:invoice_create', order.id)

    # ::# TODO: should refactor shome of the codes does not use
    if request.method == 'POST':
        isbn_search_form = BookIsbnSearchForm(data=request.POST)
        search_form = SearchForm(data=request.POST)

        if search_form.is_valid():
            search_query = search_form.cleaned_data['query']
            search_query = number_converter(search_query)
            # Here we grab the quey search from database and
            # search the fields: name, author, translator, publisher, isbn
            results = ProductSearch(
                object=Product, query=search_query).order_by('name', 'publisher')

            # if the results has only one item, the item automaticaly added to invoice
            if len(results) == 1 and not results.first().has_other_prices:
                product = results.first()
                # Check the stock of product
                variation_dict = {
                    'new': {
                        'main': {
                            'price': product.price,
                            'stock': product.stock,
                        },
                        'v1': {
                            'price': product.price_1,
                            'stock': product.stock_1,
                        },
                        'v2': {
                            'price': product.price_2,
                            'stock': product.stock_2,
                        },
                        'v3': {
                            'price': product.price_3,
                            'stock': product.stock_3,
                        },
                        'v4': {
                            'price': product.price_4,
                            'stock': product.stock_4,
                        },
                        'v5': {
                            'price': product.price_5,
                            'stock': product.stock_5,
                        },
                    },
                    'used': {
                        'main': {
                            'price': product.price_used,
                            'stock': product.stock_used
                        },
                    }
                }

                price = variation_dict[variation_list[0]
                                       ][variation_list[1]]['price']
                stock = variation_dict[variation_list[0]
                                       ][variation_list[1]]['stock']
                if price == 0:
                    messages.error(request, _(
                        'You could not add product without price'))
                    return redirect('staff:invoice_create', order_id)
                if stock <= 0:
                    messages.error(request, _('You are adding zero stock!'))

                if product.has_other_prices:
                    messages.warning(request, _(
                        'This product has other prices'))
                    # if not order:
                    #     return redirect('staff:invoice_create')
                    # if order:
                    #     return redirect('staff:invoice_create', order.id)

                # this part remove to let zero stock add
                # elif not product.has_other_prices:
                #     if product.stock <= 0:
                #         messages.error(request, _('You are adding zero stock!'))
                #         if not order:
                #             return redirect('staff:invoice_create')
                #         if order:
                #             return redirect('staff:invoice_create', order.id)

                    # if the order has not created yet, we created it here
                    if not order:
                        order = Order.objects.create(
                            user=request.user,
                            status='draft',
                            shipping_method='pickup',
                        )
                        messages.success(request,  _(
                            'Order is created') + ' : {}'.format(order.id))

                    # if the product is added in the invoice we will update the quantity in invoice
                    if (product.pk, 'new main') in product_ids and not product.has_other_prices:
                        order_line = OrderLine.objects.get(
                            order=order, product=product)
                        order_line.quantity += 1
                        order_line.variation = 'new main'
                        order_line.save()
                        order.save()

                        # Update product stock
                        product.stock -= 1
                        product.save()

                    # if the product is not in invoice we will create an invoice orderline
                    else:
                        order_line = OrderLine.objects.create(
                            order=order,
                            product=product,
                            quantity=1,
                            price=product.price,
                            variation='new main',
                            discount=0
                        )
                        order.save()

                        product.stock -= 1
                        product.save()
                    messages.success(request, _('Product is added to invoice'))
        else:
            pass

    search_form = SearchForm()

    if collection_warning:
        # collection_ids = [(id, collection_set, collection_parent), ]
        parent_ids = [ids[0] for ids in collection_ids if ids[1]]
        children_ids = [ids[0] for ids in collection_ids if ids[2]]

        collection_parent_product = Product.objects.all().filter(
            available=True).filter(pk__in=parent_ids)
        collection_children_product = Product.objects.all().filter(
            available=True).filter(pk__in=children_ids)

    return render(
        request,
        'staff/invoice_create.html',
        {'order': order,
         'isbn_search_form': isbn_search_form,
         # 'isbn': isbn,
         'product_ids': product_ids,
         'update_form': update_form,
         'search_form': search_form,
         'results': results,
         'collection_warning': collection_warning,
         'collection_parent_product': collection_parent_product,
         'collection_children_product': collection_children_product,
         })


@staff_member_required
def invoice_checkout(request, order_id, client_id=None):
    order = get_object_or_404(Order, pk=order_id)
    checkout_form = OrderAdminCheckoutForm(instance=order)
    client_search_form = ClientSearchForm()

    if client_id:
        client = CustomUser.objects.get(pk=client_id)
    elif order.client:
        client = order.client
    else:
        client = None

    credit = None
    if client:
        try:
            credit = Credit.objects.get(user=client)
        except:
            pass
    clients = None
    client_add_notice = None
    if request.method == 'POST':
        checkout_form = OrderAdminCheckoutForm(
            data=request.POST, instance=order)
        client_search_form = ClientSearchForm(data=request.POST)
        if client_search_form.is_valid():
            # messages.debug(request, 'client_search_form.is_valid')
            client_query = client_search_form.cleaned_data['client_query']

            # we will check if any farsi character is in the query we will changed it
            client_query = number_converter(client_query)
            clients = CustomUser.objects.filter(is_client=True).order_by(
                '-pk').exclude(is_superuser=True).exclude(username='guest')
            clients = clients.annotate(
                search=SearchVector('first_name', 'last_name', 'username', 'phone'),).filter(search__contains=client_query)
            if len(clients) == 0:
                client_add_notice = True

        if checkout_form.is_valid():
            if not client:
                client = CustomUser.objects.get(username='guest')
            if 'form-save' in request.POST:
                checkout_form.save()
                order.client = client
                order.save()
                return redirect('staff:invoice_checkout', order.id)

            order.client = client
            order.paid = checkout_form.cleaned_data['paid']
            order.customer_note = checkout_form.cleaned_data['customer_note']
            order.is_gift = checkout_form.cleaned_data['is_gift']
            order.channel = checkout_form.cleaned_data['channel']
            order.discount = checkout_form.cleaned_data['discount']
            order.status = 'approved'
            order.approver = request.user
            order.approved_date = datetime.now()
            order.billing_address = client.default_billing_address
            order.shipping_address = client.default_shipping_address

            if order.channel == 'cashier':
                order.shipping_method = 'pickup'
                order.shipping_status = 'full'
                order.paid = True

            order.shipping_method = checkout_form.cleaned_data['shipping_method']
            order.shipping_cost = checkout_form.cleaned_data['shipping_cost']

            order.save()
            messages.success(request, _('Order approved'))
            # return redirect('staff:order_list', period='all', channel='all')
            return redirect('staff:order_detail_for_admin', order.pk)
    return render(
        request,
        'staff/invoice_checkout.html',
        {'client_search_form': client_search_form,
         'order': order,
         'checkout_form': checkout_form,
         'clients': clients,
         'client': client,
         'client_add_notice': client_add_notice,
         'credit': credit,
         })


def invoice_checkout_credit(request, order_id, client_id):
    order = get_object_or_404(Order, pk=order_id)
    client = get_object_or_404(CustomUser, pk=client_id)
    order.client = client
    balance = client.credit.balance

    if order.payable >= balance:
        # order.discount += balance

        if order.payable == balance:
            order.paid = True

        order.pay_by_credit = True
        order.credit = balance

        order.save()

        client.credit.balance = 0
        client.credit.save()

        messages.success(request, _(
            'Credit of client added to discount of order'))
        return redirect('staff:invoice_checkout_client', order_id=order.id, client_id=client.id)

    elif order.payable < balance:
        client.credit.balance = client.credit.balance - order.payable
        # order.discount = order.payable
        order.paid = True
        order.pay_by_credit = True
        order.credit = order.payable

        order.save()
        client.credit.save()
        messages.success(request, _('Order paid with credit'))

        return redirect('staff:invoice_checkout_client', order_id=order.id, client_id=client.id)


def invoice_remove_credit(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    client = order.client

    client.credit.balance += order.credit

    order.paid = False
    order.pay_by_credit = False
    order.credit = 0
    order.save()
    client.credit.save()
    messages.success(request, _(
        'Credit remove from order and added to client credit'))
    return redirect('staff:invoice_checkout_client', order_id=order.id, client_id=client.id)


def invoice_create_add_client(request, order_id, client_id=None):
    order = get_object_or_404(Order, pk=order_id)

    # search and add client
    client_search_form = ClientSearchForm()
    client = CustomUser.objects.get(pk=client_id) if client_id else None
    client_add_notice = None
    clients = None

    if order and client:
        order.client = client
        order.billing_address = client.default_billing_address
        order.shipping_address = client.default_shipping_address
        order.save()
        messages.success(request,  _('Client added to order'))
        return redirect('staff:invoice_create', order.id)

    if request.method == 'POST':
        client_search_form = ClientSearchForm(data=request.POST)
        if client_search_form.is_valid():
            # messages.debug(request, 'client_search_form.is_valid')
            client_query = client_search_form.cleaned_data['client_query']

            # we will check if any farsi character is in the query we will changed it
            client_query = number_converter(client_query)
            clients = CustomUser.objects.filter(is_client=True).order_by(
                '-pk').exclude(is_superuser=True).exclude(username='guest')
            clients = clients.annotate(
                search=SearchVector('first_name', 'last_name', 'username', 'phone'),).filter(search__contains=client_query)
            if len(clients) == 0:
                client_add_notice = True

    # return redirect('staff:invoice_create', order_id=order.id)
    return render(
        request,
        'staff/order_add_client.html',
        {
            'client_search_form': client_search_form,
            'client_add_notice': client_add_notice,
            'clients': clients,
            'order': order,
        }
    )


@staff_member_required
def remove_client_from_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    if order.credit:
        # remove credit from order
        client = order.client

        client.credit.balance += order.credit

        order.paid = False
        order.pay_by_credit = False
        order.credit = 0
        order.save()
        client.credit.save()
        messages.success(request, _(
            'Credit remove from order and added to client credit'))

    order.client = None
    order.save()
    messages.success(request, _('Client removed from order'))
    return redirect('staff:invoice_checkout', order.id)


@staff_member_required
def orderline_update(request, order_id, orderline_id):
    update_form = InvoiceAddForm(initial={'quantity': "0"})
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        update_form = InvoiceAddForm(data=request.POST)
        if update_form.is_valid():
            order_line = OrderLine.objects.get(pk=orderline_id)

            product = order_line.product
            variation = order_line.variation

            # to work with orderlines that have been made before
            if variation == 'main':
                variation = 'new main'
            elif variation == 'v1':
                variation = 'new v1'
            elif variation == 'used':
                variation = 'used main'
            order_line.variation = variation
            order_line.save()

            variation_list = variation.split()
            variation_dict = {
                'new': {
                    'main': {
                        'price': product.price,
                        'stock': product.stock,
                    },
                    'v1': {
                        'price': product.price_1,
                        'stock': product.stock_1,
                    },
                    'v2': {
                        'price': product.price_2,
                        'stock': product.stock_2,
                    },
                    'v3': {
                        'price': product.price_3,
                        'stock': product.stock_3,
                    },
                    'v4': {
                        'price': product.price_4,
                        'stock': product.stock_4,
                    },
                    'v5': {
                        'price': product.price_5,
                        'stock': product.stock_5,
                    },
                },
                'used': {
                    'main': {
                        'price': product.price_used,
                        'stock': product.stock_used
                    },
                }
            }

            product_price = variation_dict[variation_list[0]
                                           ][variation_list[1]]['price']
            product_stock = variation_dict[variation_list[0]
                                           ][variation_list[1]]['stock']

            if update_form.cleaned_data['remove'] == True:
                """
                remove an orde line if remove checkbox is clicked
                """
                # Update product stock
                product_stock += order_line.quantity
                # if product_stock < 0:
                # else:
                #     product_stock += order_line.quantity
                # product_stock += order_line.quantity

                # if variation == 'main':
                #     product.stock = product_stock
                # elif variation  == 'v1':
                #     product.stock_1 = product_stock
                # elif variation == 'used':
                #     product.stock_used = product_stock
                # we have some old row in purchase lines
                if variation == 'new main':
                    product.stock = product_stock

                elif variation == 'new v1':
                    product.stock_1 = product_stock

                elif variation == 'new v2':
                    product.stock_2 = product_stock

                elif variation == 'new v3':
                    product.stock_3 = product_stock

                elif variation == 'new v3':
                    product.stock_4 = product_stock

                elif variation == 'new v4':
                    product.stock_5 = product_stock

                elif variation == 'used main':
                    product.stock_used = product_stock

                product.save()

                order_line.delete()
                order.save()
                return redirect('staff:invoice_create', order.id)

            if update_form.cleaned_data['quantity'] != 0:
                # increase the quantity of product in invoice
                if update_form.cleaned_data['quantity'] > order_line.quantity:
                    if update_form.cleaned_data['quantity'] > order_line.quantity + product_stock:
                        # return redirect('staff:invoice_create', order.id)
                        messages.error(request, _('You are adding zero stock'))

                    # Update product stock
                    if product_stock < 0:
                        product_stock = product_stock + order_line.quantity - \
                            update_form.cleaned_data['quantity']
                    else:
                        product_stock -= update_form.cleaned_data['quantity'] - \
                            order_line.quantity

                    # if variation == 'main':
                    #     product.stock = product_stock
                    # elif variation  == 'v1':
                    #     product.stock_1 = product_stock
                    # elif variation == 'used':
                    #     product.stock_used = product_stock
                    if variation == 'new main':
                        product.stock = product_stock

                    elif variation == 'new v1':
                        product.stock_1 = product_stock

                    elif variation == 'new v2':
                        product.stock_2 = product_stock

                    elif variation == 'new v3':
                        product.stock_3 = product_stock

                    elif variation == 'new v3':
                        product.stock_4 = product_stock

                    elif variation == 'new v4':
                        product.stock_5 = product_stock

                    elif variation == 'used main':
                        product.stock_used += product_stock

                    product.save()
                    messages.success(request, _(
                        'Order line updated') + ' ' + _('Quantity') + ' {}'.format(product_stock))

                elif update_form.cleaned_data['quantity'] < order_line.quantity:
                    # Update product stock
                    product_stock += order_line.quantity - \
                        update_form.cleaned_data['quantity']
                    # if product_stock < 0:
                    #     product_stock += order_line.quantity + update_form.cleaned_data['quantity']
                    # else:
                    #     product_stock += order_line.quantity - update_form.cleaned_data['quantity']

                    if variation == 'new main':
                        product.stock = product_stock

                    elif variation == 'new v1':
                        product.stock_1 = product_stock

                    elif variation == 'new v2':
                        product.stock_2 = product_stock

                    elif variation == 'new v3':
                        product.stock_3 = product_stock

                    elif variation == 'new v3':
                        product.stock_4 = product_stock

                    elif variation == 'new v4':
                        product.stock_5 = product_stock

                    # we have some old row in purchase lines
                    elif variation == 'used main':
                        product.stock_used += product_stock

                    product.save()

                order_line.quantity = update_form.cleaned_data['quantity']
                order_line.save()
                order.save()
                return redirect('staff:invoice_create', order.id)
            if update_form.cleaned_data['discount'] != 0:
                order_line.discount = update_form.cleaned_data['discount']
                order_line.save()
                order.save()
            elif update_form.cleaned_data['discount'] == 0:
                order_line.discount = update_form.cleaned_data['discount']
                order_line.save()
                order.save()
            update_form = InvoiceAddForm()
            return redirect('staff:invoice_create', order.id)

    return render(
        request,
        'staff/invoice_create.html',
        {'update_form': update_form}
    )


@staff_member_required
def draft_orders(request):
    # draft_orders = Order.objects.filter(status='draft').exclude(quantity=0)
    draft_orders = Order.objects.filter(status='draft').filter(active=True)

    return render(
        request,
        'staff/draft_orders.html',
        {'draft_orders': draft_orders}
    )


@staff_member_required
def remove_draft_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if len(order.lines.all()) > 0:
        messages.error(request, _('This order is not empty'))
    else:
        # order.delete()
        order.active = False
        order.customer_note = f"removed by {request.user}"
        order.save()
        messages.success(request, _('Draft order removed'))

    return redirect('staff:draft_orders')


@staff_member_required
def invoice_back_to_draft(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if order.shipping_status == 'full':
        messages.warning(request, _('This order is shipped'))
    if order.is_packaged:
        messages.warning(request, _('This order is completely packaged'))
        subject = '[Warning] ' + 'A packaged order is changed'
        message = f"A packaged order send back to draft \nOrder no.: {order_id} \nClient: {order.client.first_name} {order.client.last_name}"
        recivers = ['rahim.aghareb@gmail.com', 'mahazr77@gmail.com']
        notif_email_to_managers(subject, message, recivers)

    order.approver = None
    order.approved_date = None
    order.status = 'draft'
    order.shipping_status = ''
    order.is_packaged = False
    order.save()
    messages.success(request, _('Order status changed to draft'))
    return redirect('staff:invoice_checkout', order.id)


def order_payment_manage(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        payment_form = OrderPaymentManageForm(
            request.POST, files=request.FILES, instance=order)
        if payment_form.is_valid():
            payment_form.save()
            return redirect('staff:order_detail_for_admin', order.id)

    else:
        payment_form = OrderPaymentManageForm(instance=order)
    return render(
        request,
        'staff/order_payment_manage.html',
        {
        'order': order,
        'payment_form': payment_form,
        }
    )


@staff_member_required
def category_list(request):
    main_categories = Category.objects.filter(
        active=True, parent_category=None)

    return render(
        request,
        'staff/categories.html',
        {'main_categories': main_categories}
    )


@staff_member_required
def sold_products(request, days=None, date=None, period=None):
    # print(date)
    date_raw = date
    fa_date = None
    if days:
         # use cache to reduce queries
        order_lines = cache.get('order_lines_book_days_{}'.format(days))
        if not order_lines:
            order_lines = OrderLine.objects.all().filter(active=True).filter(created__gte=datetime.now(
            ) - timedelta(days)).exclude(product__product_type='craft').order_by('-created')
            cache.set('order_lines_book_days_{}'.format(days), order_lines)

    if date:
        date = datetime.strptime(date, "%Y%m%d").date()
        fa_date = hij_strf_date(greg_to_hij_date(date), '%-d %B %Y')

         # use cache to reduce queries
        order_lines = cache.get('order_lines_book_date_{}'.format(date_raw))
        if not order_lines:
            order_lines = OrderLine.objects.all().filter(active=True).filter(
                created__date=date).exclude(product__product_type='craft').order_by('-created')
            cache.set('order_lines_book_date_{}'.format(date_raw), order_lines)
        # print(len(order_lines))
        # all_payment = Payment.objects.filter(created__date__gte='2022-02-01').aggregate(total_amount=Sum('amount'))
    if period:
        period_list = period.split('-')
        start = datetime.strptime(period_list[0], "%Y%m%d").date()
        end = datetime.strptime(period_list[1], "%Y%m%d").date()

         # use cache to reduce queries
        order_lines = cache.get('order_lines_book_{}'.format(period))
        if not order_lines:
            order_lines = OrderLine.objects.all().filter(active=True).filter(
                created__date__range=(start, end)).exclude(product__product_type='craft').order_by('-created')
            cache.set('order_lines_book_{}'.format(period), order_lines)

    # object_list = order_lines

    paginator = Paginator(order_lines, 50) # 9 products in each page
    page = request.GET.get('page')
    try:
        order_lines = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        order_lines = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        order_lines = paginator.page(paginator.num_pages)

    # order_lines = OrderLine.objects.all().values_list(product.id, flat=True)
    products = dict()
    main_stock = dict()
    check_list = []
    added_line = {}
    # added_line = {
    #     'pk': {
    #         'quantity': 'x',
    #         'name': 'str',
    #         'created': 'created',
    #         'stock': 'y',
    #          'variation': 'new main'
    #          'id': 'id'
    #     }
    # }
    for item in order_lines:
        vendors_list = item.product.vendors.all().values_list('first_name', flat=True)
        # print(vendors_list)

        # vendors_list = [item.first_name for item in vendors]
        # key = products.get(item.product.id)
        # print(item.product.id)
        # if item.product.name in added_line:
        if str(item.product.id) in added_line:
            added_line[str(item.product.id)]['quantity'] += item.quantity
            pass
        else:
            # messages.warning(request, 'hi')
            # check_list.append(item.product.name)
            added_line[str(item.product.id)] = {
                'name': str(item.product),
                'quantity': item.quantity,
                'created': hij_strf_date(greg_to_hij_date(item.created.date()), '%-d %B %Y'),
                'stock': item.product.stock,
                'variation': item.variation,
                'isbn': item.product.isbn,
                'id': item.product.id,
                'publisher': item.product.pub_1 if item.product.pub_1 else '',
                'vendors': vendors_list,
                }

    return render(
        request,
        'staff/sold_products.html',
        {
            'order_lines': order_lines,
             'products': products,
             'main_stock': main_stock,
             'added_line': added_line,
             'check_list': check_list,
             'date': date,
             'date_raw': date_raw,
             'days': days,
             'fa_date': fa_date,
             'period': period,
             'page': page,
         }
    )


@staff_member_required
def purchased_products(request):

    purchase_lines = PurchaseLine.objects.all().filter(
        active=True).order_by('purchase__created')

    # order_lines = OrderLine.objects.all().values_list(product.id, flat=True)
    products = dict()
    i = 0
    for line in purchase_lines:

        if line.product.name in products:
            # we grab the present value from the products dictionary
            quantity = products[line.product.name]['quantity']
            vendor = products[line.product.name]['vendor']

            # wether vendor in list is as the same as the vendor in orderline
            if vendor == line.purchase.vendor.first_name:
                quantity += line.quantity
                products[line.product.name] = {
                    'quantity': quantity,
                    'vendor': vendor
                }
            # wether the vendor is diffrent from the vendor in order line
            else:
                # this line makes a bug and override the availabel book not add a new line
                products[line.product.name + str(i)] = {
                    'quantity': line.quantity,
                    'vendor': line.purchase.vendor.first_name
                }

        else:
            products[line.product.name] = {
                'quantity': line.quantity,
                'vendor': line.purchase.vendor.first_name
            }
        i += 1
    # products = sorted(products.lines(), key=lambda x: x[0], reverse=True)

    # test = {
    #     'book_name':{
    #         'quantity': 25,
    #         'vendor': 'shola'
    #     },
    #     'book_name2':{
    #         'quantity': 25,
    #         'vendor': 'shola'
    #     }
    # }
    return render(
        request,
        'staff/purchased_products.html',
        {
            'purchase_lines': purchase_lines,
            'products': products,
            # 'test': test,
        }
    )


@staff_member_required
def vendor_add(request):
    vendor_form = VendorAddForm()
    address_form = VendorAddressAddForm(
        initial={'country': 'IR', 'city': _('Tehran')})
    if request.method == 'POST':
        vendor_form = VendorAddForm(request.POST)
        address_form = VendorAddressAddForm(request.POST)
        if vendor_form.is_valid() and address_form.is_valid():
            vendor = vendor_form.save(commit=False)
            vendor.username = vendor_form.cleaned_data['first_name']

            address = address_form.save(commit=False)
            address.phone = vendor.phone
            address.name = vendor.username
            address.save()  # we should save and create the address then add it to vendor

            vendor.default_billing_address = address
            vendor.email = '{}@ketabedamavand.com'.format(vendor.username)

            vendor.save()

            messages.success(request, _('Vendor is added!') +
                             ' {}'.format(vendor.first_name))

            return HttpResponseRedirect(reverse('staff:vendor_list'))
        else:
            messages.error(request, _('Form is not valid'))
    else:
        vendor_form = VendorAddForm()
        address_form = VendorAddressAddForm(
            initial={'country': 'IR', 'city': _('Tehran')})
    return render(
        request,
        'staff/vendor_add.html',
        {'vendor_form': vendor_form,
         'address_form': address_form}
    )


@staff_member_required
def vendor_edit(request, vendor_id):
    vendor = get_object_or_404(Vendor, pk=vendor_id)
    if request.method == 'POST':
        vendor_form = VendorAddForm(request.POST, instance=vendor)
        address_form = VendorAddressAddForm(
            request.POST, instance=vendor.default_billing_address)
        if vendor_form.is_valid() and address_form.is_valid():
            vendor_form.save()
            address_form.save()
            messages.success(request, _('Vendor is updated') +
                             ': {}'.format(vendor.first_name))
        else:
            messages.error(request, _('Form is not valid'))
    else:
        vendor_form = VendorAddForm(instance=vendor)
        address_form = VendorAddressAddForm(
            instance=vendor.default_billing_address)
    return render(
        request,
        'staff/vendor_add.html',
        {'vendor_form': vendor_form,
         'address_form': address_form}
    )


@staff_member_required
def vendor_list(request):
    vendors = Vendor.objects.all()
    return render(
        request,
        'staff/vendor_list.html',
        {'vendors': vendors}
    )


@staff_member_required
def order_shipping(request, order_id):
    form_submit = False
    order = get_object_or_404(Order, pk=order_id)
    shipping_form = OrderShippingForm(instance=order)
    if request.method == 'POST':
        shipping_form = OrderShippingForm(data=request.POST, instance=order)
        if shipping_form.is_valid():
            form = shipping_form.save(commit=False)
            if form.is_packaged:
                order.packaged_quantity = order.quantity
            # order.status = shipping_form.cleaned_data['shipping_status']
            # order.shipped_code = shipping_form.cleaned_data['shipped_code']
            if form.shipping_status == 'full':
                order.full_shipped_date = datetime.now()
            form.save()
            order.save()
            form_submit = True
            messages.success(request, 'Shipping status is updated')
            messages.warning(request, 'Update the order list')
            # return redirect('staff:order_shipped', order.id)

    else:
        shipping_form = OrderShippingForm(instance=order)

    return render(
        request,
        'staff/order_shipped.html',
        {'order': order,
         'shipping_form': shipping_form,
         'form_submit': form_submit}
    )


@staff_member_required
def order_list_by_country(request, country_code=None):
    orders = Order.objects.all().exclude(channel='cashier').filter(
        Q(status='approved') | Q(status='paid')).filter(active=True)

    countries = set(
        list(filter(None, Address.objects.all().values_list('country', flat=True))))

    country = None
    if country_code:
        orders = orders.filter(billing_address__country=country_code)
        country = Country(code=country_code)
    return render(
        request,
        'staff/order_list_by_country.html',
        {
            'orders': orders,
            'countries': countries,
            'country': country,
        }
    )


@staff_member_required
def collection_management(request):
    products_object = Product.objects.all().filter(available=True)

    search_form = SearchForm()
    if request.method == 'POST':
        search_form = SearchForm(data=request.POST)
        if search_form.is_valid():
            search_query = search_form.cleaned_data['query']

            products_object = ProductSearch(
                object=Product, query=search_query).order_by('name', 'publisher')

    # pagination
    paginator = Paginator(products_object, 50)  # 50 posts in each page
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        products = paginator.page(paginator.num_pages)

    return render(
        request,
        'staff/collection_management.html',
        {
            'products': products,
            'page': page,
            'search_form': search_form,
        }
    )


@staff_member_required
def collection_management_edit(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if product.collection_set:
        product_isbn = product.collection_set.split()
        products = Product.objects.all().filter(available=True).filter(
            isbn__in=product_isbn).order_by('name')
    else:
        products = None
        product_isbn = []
    collection_form = ProductCollectionForm()
    if request.method == 'POST':
        collection_form = ProductCollectionForm(data=request.POST)
        if collection_form.is_valid():
            isbn = collection_form.cleaned_data['collection_field']
            if isbn in product_isbn:
                messages.warning(request, _(
                    'This product is in this collection'))
                return redirect('staff:collection_management_edit', product.id)
            new_product = None
            try:
                new_product = get_object_or_404(Product, isbn=isbn)
            except:
                messages.error(request, _('Product does not found'))
            if new_product:
                new_collection_set = f"{product.collection_set} {isbn}"
                product.collection_set = new_collection_set
                new_product.is_collection = True
                new_product.collection_parent = product.isbn

                product.save()
                new_product.save()

                messages.success(request, _('The product added to collection'))
                return redirect('staff:collection_management_edit', product.id)
    return render(
        request,
        'staff/collection_management_edit.html',
        {
            'product': product,
            'products': products,
            'collection_form': collection_form,
        }
    )


@staff_member_required
def collection_management_remove(request, product_id, product_isbn):
    product = get_object_or_404(Product, pk=product_id)
    removed_product = get_object_or_404(Product, isbn=product_isbn)

    product_isbn_list = product.collection_set.split()
    print(product_isbn_list)
    product_isbn_list.remove(product_isbn)
    product.collection_set = ' '.join(product_isbn_list)

    product.save()

    removed_product.is_collection = False
    removed_product.collection_parent = None
    removed_product.save()
    messages.success(request, _('This product removed from the collection'))
    return redirect('staff:collection_management_edit', product.id)


def zero_stock_list(request):
    products = Product.objects.all().filter(
        available=True).filter(stock__lte=0).order_by('stock')
    return render(
        request,
        'staff/zero_stock_list.html',
        {
            'products': products,
        }
    )


@staff_member_required
def used_book_prices(request, product_id):
    product = Product.objects.get(pk=product_id)
    half_price = 0
    price_offers = []
    if product.price:
        half_price = product.price / 2
    else:
        price_offers = [
            # round(product.page_number / 10 ) * 15000,
            round(product.page_number *  0.13) * 10000,
            round(product.page_number *  0.15) * 10000,
            round(product.page_number *  0.17) * 10000,
        ]
        # price_offers.sort()
    if request.method == 'POST':
        price_form = AdminPriceManagementForm(
            data=request.POST, instance=product)
        if price_form.is_valid():
            used_price = price_form.save(commit=False)
            if 'offer' in request.POST:
                data = request.POST.dict()
                offer = Decimal(data.get("offer").replace(',', ''))
                used_price.price_used = offer
            else:
                offer = used_price.price_used
            used_price.save()
            messages.success(request, _('Used price for product updated') + f": {product.name} - {offer} " + _('Rial'))
            return redirect('staff:products')
    else:
        price_form = AdminPriceManagementForm(instance=product)
    return render(
        request,
        'staff/used_book_prices.html',
        {
            'product': product,
            'price_form': price_form,
            'half_price': half_price,
            'price_offers': price_offers,
        }
    )


@staff_member_required
def product_stock_price_edit(request, product_id):
    product = Product.objects.get(pk=product_id)
    stock = product.stock
    price = product.price
    if request.method == 'POST':
        if request.user.is_online_manager:
            price_form = OnlineAdminPriceStockManagementForm(
                data=request.POST, instance=product)
        else:
            price_form = AdminPriceStockManagementForm(
                data=request.POST, instance=product)
        if price_form.is_valid():
            #  we want to check wether the newly entered stock more than DB stock or not
            # if it is more we make a purchase for editing tne DB
            new_price_stock = price_form.save(commit=False)

            # check the price is the biggest price of product
            if new_price_stock.price < price:
                messages.error(request, _(
                    'You could not enter a price less than the main price '))
                return redirect('staff:product_stock_price_edit', product.id)

            if request.user.is_online_manager:
                new_price_stock.save()
                messages.success(request, _('Price updated'))
                return redirect('staff:products')

            if new_price_stock.stock > stock:
                messages.warning(request, _(
                    'A purchase added to manage the DB'))

                # grab the vendor
                try:
                    vendor = Vendor.objects.get(first_name='Stock-admin')
                except:
                    vendor = Vendor.objects.create(
                        first_name='Stock-admin',
                        username='Stock-admin',
                        email='stock.admin@ketabedamavand.com'
                    )
                    vendor.save()

                # Making a new purchase
                purchase = Purchase.objects.create(
                    vendor=vendor,
                    registrar=request.user,
                    approver=request.user,
                    approved_date=datetime.now(),
                    payment_date=datetime.now().date(),
                    paper_invoice_number='stock-balance',
                    status='approved',
                    discount_percent=100,

                )
                purchase.save()
                #  Add a purchaseline for newly added stock
                purchaseline = PurchaseLine.objects.create(
                    purchase=purchase,
                    product=product,
                    price=product.price,
                    quantity=new_price_stock.stock - stock,
                    variation='new main',
                    active=True
                )
                purchaseline.save()
                purchase.save()

            # check if the used price or stock is changed check has other prices
            if new_price_stock.price_used or new_price_stock.stock_used:
                product.has_other_prices = True
                product.save()
            if new_price_stock.price_used == 0 and new_price_stock.stock_used == 0:
                if product.stock_1 == 0 and product.stock_2 == 0 and product.stock_3 == 0 and product.stock_4 == 0 and product.stock_5 == 0:
                    if product.price_1 == 0 and product.price_2 == 0 and product.price_3 == 0 and product.price_4 == 0 and product.price_5 == 0:
                        product.has_other_prices = False
                        product.save()

            new_price_stock.save()
            messages.success(request, _('Stock and price updated'))
            return redirect('staff:products')

    else:
        if request.user.is_online_manager:
            price_form = OnlineAdminPriceStockManagementForm(instance=product)
        else:
            price_form = AdminPriceStockManagementForm(instance=product)
    return render(
        request,
        'staff/product_stock_price_edit.html',
        {
            'product': product,
            'price_form': price_form,
        }
    )


@staff_member_required
def craft_list(request):
    crafts = Product.objects.filter(available=True).filter(
        product_type='craft').order_by('category', 'name')
    return render(
        request,
        'staff/crafts/craft_list.html',
        {
            'crafts': crafts,
        }
    )


@staff_member_required
def craft_update(request, craft_id=None):
    if craft_id:
        craft = get_object_or_404(Product, pk=craft_id)
    else:
        craft = None
    if request.method == 'POST':
        if craft_id:
            update_form = CraftUpdateForm(data=request.POST, instance=craft)
        else:
            update_form = CraftUpdateForm(data=request.POST)

        if update_form.is_valid():
            new_product = update_form.save(commit=False)
            new_product.product_type = 'craft'
            new_product.available_online = False
            new_product.save()
            messages.success(request, _('New craft is created'))
            return redirect('staff:craft_list')
    else:
        if craft_id:
            update_form = CraftUpdateForm(instance=craft)
        else:
            update_form = CraftUpdateForm()

    return render(
        request,
        'staff/crafts/craft_update.html',
        {
            'craft': craft,
            'update_form': update_form,
        }
    )


@staff_member_required
def product_price_show(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(
        request,
        'staff/product_price_show.html',
        {
        'product': product,
        }
    )


@staff_member_required
def full_shipped_list(request, date=None):
    if date:
        try:
            date = datetime.strptime(date, "%Y%m%d").date()
        except ValueError:
            messages.error(request, _('Date is not valid'))
            return redirect('staff:full_shipped_list')
        fa_date = hij_strf_date(greg_to_hij_date(date), '%-d %B %Y')
        orders = Order.objects.filter(active=True).filter(full_shipped_date__date=date).filter(
            full_shipped_date__isnull=False).filter(shipping_method='bike_delivery')
    else:
        orders = Order.objects.filter(active=True).filter(
            full_shipped_date__isnull=False).filter(shipping_method='bike_delivery')
    # sum of shipping cost and shipping cost with 15% discount
    shipping_cost_sum = {}
    if orders:
        shipping_cost_sum = orders.aggregate(total=Sum(
            'shipping_cost'), total_discount=Sum('shipping_cost') * Decimal(0.85))
        shipping_cost_sum['total_discount'] = round(
            shipping_cost_sum['total_discount'])
    else:
        shipping_cost_sum['total'] = 0
        shipping_cost_sum['total_discount'] = 0
    return render(
        request,
        'staff/full_shipped_list.html',
        {
            'orders': orders,
            'date': date,
            'shipping_cost_sum': shipping_cost_sum,
        }
    )


@staff_member_required
def sales_by_vendor(request, vendor_id=None, date='20220220-20220320'):
    vendor = None
    orderlines = None
    more_vendor = False
    # purchaselines = None
    results = {}
    # results_p = {}
    product_counts = 0
    # product_counts_p = 0
    total_cost = 0
    vendors = Vendor.objects.all()
    if vendor_id:
        vendor = get_object_or_404(Vendor, pk=vendor_id)
        dates = list(date.split('-'))

        start_date = datetime.strptime(dates[0], "%Y%m%d").date()
        end_date = datetime.strptime(dates[1], "%Y%m%d").date()
        orderlines = OrderLine.objects.filter(product__vendors=vendor).filter(created__date__gte=start_date, created__date__lte=end_date)

        # orderlines_list = orderlines.values_list('product__id', flat=True)
        # purchaselines = PurchaseLine.objects.filter(purchase__vendor=vendor)

    # if purchaselines:
    #     product_counts_p = purchaselines.aggregate(total=Sum('quantity'))
    #     for line in purchaselines.iterator():
    #         if line.product.pk not in results_p:
    #             results_p[line.product.pk] = {
    #                 'name': line.product.name,
    #                 'quantity': line.quantity,
    #                 'price': [line.price],
    #                 'cost': line.get_cost_after_discount()
    #             }
    #         else:
    #             results_p[line.product.pk]['quantity'] += line.quantity
    #             results_p[line.product.pk]['cost'] += line.get_cost_after_discount()
    #             if line.price not in results_p[line.product.pk]['price']:
    #                 results_p[line.product.pk]['price'].append(line.price)
    if orderlines:
        product_counts = orderlines.aggregate(total=Sum('quantity'))

        for line in orderlines.iterator():
            if line.product.vendors.count() > 1:
                more_vendor = True
            if line.product.pk not in results:
                results[line.product.pk] = {
                    'name': line.product.name,
                    'quantity': line.quantity,
                    'price': [line.price],
                    'cost': line.get_cost_after_discount(),
                    'vendors': line.product.vendors.all()
                    # 'more_vendor': more_vendor
                }
            else:
                results[line.product.pk]['quantity'] += line.quantity
                results[line.product.pk]['cost'] += line.get_cost_after_discount()
                if line.price not in results[line.product.pk]['price']:
                    results[line.product.pk]['price'].append(line.price)
            total_cost += line.get_cost_after_discount()
            results[line.product.pk]['more_vendor'] = more_vendor
    return render(
        request,
        'staff/sales_by_vendor.html',
        {
            'products': products,
            'vendor': vendor,
            'vendors': vendors,
            'orderlines': orderlines,
            'results': results,
            'product_counts': product_counts,
            'total_cost': total_cost,
            # 'purchaselines': purchaselines,
            # 'results_p': results_p,
            # 'product_counts_p': product_counts_p,
        }
    )


@staff_member_required
def product_reports(request):
    products = Product.objects.filter(available=True).exclude(product_type='craft').filter(Q(stock__gte=1) | Q(stock_1__gte=1) | Q(stock_2__gte=1) | Q(stock_3__gte=1) | Q(stock_4__gte=1) | Q(stock_5__gte=1))

    new_products = products.order_by('name', 'publisher')

    new_products_quantity_0 = products.aggregate(total=Sum('stock'))
    new_products_quantity_1 = products.aggregate(total=Sum('stock_1'))
    new_products_quantity_2 = products.aggregate(total=Sum('stock_2'))
    new_products_quantity_3 = products.aggregate(total=Sum('stock_3'))
    new_products_quantity_4 = products.aggregate(total=Sum('stock_4'))
    new_products_quantity_5 = products.aggregate(total=Sum('stock_5'))
    new_products_quantity = sum([
        new_products_quantity_0['total'],
        new_products_quantity_1['total'],
        new_products_quantity_2['total'],
        new_products_quantity_3['total'],
        new_products_quantity_4['total'],
        new_products_quantity_5['total']
    ])

    used_products = Product.objects.filter(available = True).exclude(product_type = 'craft').filter(
        stock_used__gte = 1).exclude(product_type = 'craft').order_by('name', 'publisher')
    used_products_quantity = Product.objects.filter(available = True).exclude(product_type = 'craft').filter(
        stock_used__gte = 1).exclude(product_type = 'craft').aggregate(total = Sum('stock_used'))

    new_products_counts = new_products.count()
    used_products_counts = used_products.count()
    all_quantity = new_products_counts + used_products_counts



    crafts_counts=Product.objects.filter(available = True).filter(
        product_type = 'craft').filter(stock__gte = 1).count()
    crafts_counts_quantity=Product.objects.filter(available = True).filter(
        product_type = 'craft').filter(stock__gte = 1).aggregate(total = Sum('stock'))

    return render(
        request,
        'staff/product_reports.html',
        {
            'new_products_counts': new_products_counts,
            'new_products_quantity': new_products_quantity,
            'used_products_counts': used_products_counts,
            'used_products_quantity': used_products_quantity,
            'all_quantity': all_quantity,
            'all_stock': new_products_quantity + used_products_quantity['total'],
            'crafts_counts': crafts_counts,
            'crafts_counts_quantity': crafts_counts_quantity,
        }
    )


@staff_member_required
def image_management(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    images = product.images.all()
    if request.method == 'POST':
        image_form = ProductImageManagementForm(
            data=request.POST,
            # instance=product,
            files=request.FILES
        )
        if image_form.is_valid():
            new_image = image_form.save(commit=False)
            new_image.product = product
            new_image.registrar = request.user

            #  renaming the file
            file = request.FILES['file']
            file.name = f"{product.id}-{random.randint(10,99)}{random.randint(10,99)}.{file.name.split('.')[1]}"
            new_image.file = file

            # Set the Image name field
            new_image.name = file.name.split('.')[0]

            if not new_image.image_alt:
                new_image.image_alt = str(product)

            if not images:
                new_image.main_image = True
                product.image = new_image.file
                product.save()

            new_image.save()
            messages.success(request, _('Image added to product'))
            if 'another' in request.POST:
                return redirect('staff:image_management', product.id)
            return redirect('staff:products')
    else:
        image_form = ProductImageManagementForm()

    return render (
        request,
        'staff/products/image_management.html',
        {
            'images': images,
            'image_form': image_form,
            'product_id': product.id,
            'product': {'name': product, 'id': product.id, 'isbn':product.isbn}
        }
    )

@staff_member_required
def image_remove(request, image_id, product_id):
    product = get_object_or_404(Product, pk=product_id)

    image = get_object_or_404(Image, pk=image_id)
    if image.main_image:
        product.image = None

    image.delete()
    messages.success(request, _('Image is removed'))
    images = product.images.all()
    if images:
        new_main_image = images.first()
        new_main_image.main_image = True
        new_main_image.save()
        product.image = new_main_image.file

    product.save()

    return redirect('staff:image_management', product_id )
