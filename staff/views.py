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

from django_countries.fields import Country

from .forms import ProductCreateForm, OrderCreateForm, InvoiceAddForm, CategoryCreateForm, OrderShippingForm, ProductCollectionForm
from products.models import Product, Category
from orders.models import Order, OrderLine, PurchaseLine
from orders.forms import OrderAdminCheckoutForm, OrderPaymentManageForm
from search.forms import ClientSearchForm, BookIsbnSearchForm, SearchForm
from search.views import ProductSearch
from account.models import CustomUser, Vendor, Address, Credit
from account.forms import VendorAddForm, AddressAddForm, VendorAddressAddForm
from tools.fa_to_en_num import number_converter


def sales(request):
    return render(
        request,
        'staff/sales.html',
        {}
    )


@staff_member_required
def orders(request, period=None, channel=None):
    # list of all approved or paid orders
    if channel == 'all' and period == 'all':
        orders = Order.objects.filter(
            Q(status='approved') | Q(paid=True)).filter(active=True)

    # 'mix' channel means we need the orders that should be collected
    if channel == 'mix' and period == 'all':
        # orders = Order.objects.filter(
        #     Q(status='approved') | Q(paid=True)).exclude(channel='cashier')
        orders = Order.objects.exclude(
            channel='cashier').exclude(status='draft').filter(active=True)

    # staff/orders/30/mix
    elif channel == 'mix' and period not in ('all', 'mix'):
        orders = Order.objects.filter(
            Q(status='approved') | Q(paid=True)).exclude(channel='cashier').filter(approved_date__gte=datetime.now() - timedelta(int(period))).filter(active=True)

    # staff/orders/365/cashier
    elif channel == 'cashier' and period not in ('all', 'mix'):
        orders = Order.objects.filter(
            Q(status='approved') | Q(paid=True)).filter(channel='cashier').filter(approved_date__gte=datetime.now() - timedelta(int(period))).filter(active=True)
    else:
        orders = Order.objects.filter(
            Q(status='approved') | Q(paid=True)).filter(active=True)

    return render(
        request,
        'staff/orders.html',
        {'orders': orders}
    )


@staff_member_required
def order_detail_for_admin(request, pk):
    order = get_object_or_404(Order, pk=pk)
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
        'staff/products.html',
        {
            'products': products,
            'page': page,
            'search_form': search_form,
        }
    )


@staff_member_required
def product_create(request):
    if request.method == 'POST':
        form = ProductCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Product is created!'))
            if 'another' in request.POST:
                return HttpResponseRedirect(reverse('staff:product_create'))
            return HttpResponseRedirect(reverse('staff:products'))
        else:
            messages.error(request, _('Form is not valid'))
    else:
        form = ProductCreateForm()
    return render(
        request,
        'staff/product_create.html',
        {'form': form}
    )


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
        order = Order.objects.get(pk=order_id)
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
            product.stock_used += stock
        product.save()

        messages.success(request, _('Product is added to invoice'))

        return redirect('staff:invoice_create', order.id)

    # When we add a product for first time and we dont have an order
    if (not order_id) and product_id:
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
            product.stock_used += stock

        product.save()

        messages.success(request,  _('Product is added to invoice'))
        return redirect('staff:invoice_create', order.id)

    # ::# TODO: should refactor shome of the codes does not use
    if request.method == 'POST':
        isbn_search_form = BookIsbnSearchForm(data=request.POST)
        search_form = SearchForm(data=request.POST)

        if search_form.is_valid():
            search_query = search_form.cleaned_data['query']

            # Here we grab the quey search from database and
            # search the fields: name, author, translator, publisher, isbn
            results = ProductSearch(
                object=Product, query=search_query).order_by('name', 'publisher')

            # if the results has only one item, the item automaticaly added to invoice
            if len(results) == 1:
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
                            variation='new main'
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

        collection_parent_product = Product.objects.all().filter(available=True).filter(pk__in=parent_ids)
        collection_children_product = Product.objects.all().filter(available=True).filter(pk__in=children_ids)

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
    order = Order.objects.get(pk=order_id)
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
    order = Order.objects.get(pk=order_id)
    client = CustomUser.objects.get(pk=client_id)
    order.client = client
    balance = client.credit.balance

    if order.payable >= balance:
        order.discount = balance

        if order.payable == balance:
            order.paid = True
        order.pay_by_credit = True
        order.credit = balance

        order.save()

        client.credit.balance = 0
        client.credit.save()
        messages(request, _('Credit of client added to discount of order'))
        return redirect('staff:invoice_checkout_client', order_id=order.id, client_id=client.id)

    elif order.payable < balance:
        client.credit.balance = client.credit.balance - order.payable
        order.discount = order.payable
        order.paid = True
        order.pay_by_credit = True
        order.credit = balance

        order.save()
        client.credit.save()
        messages(request, _('Order paid with credit'))

        return redirect('staff:invoice_checkout_client', order_id=order.id, client_id=client.id)


def invoice_create_add_client(request, order_id, client_id=None):
    order = Order.objects.get(pk=order_id)

    # search and add client
    client_search_form = ClientSearchForm()
    client = CustomUser.objects.get(pk=client_id) if client_id else None
    client_add_notice = None
    clients = None

    if order and client:
        order.client = client
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
def orderline_update(request, order_id, orderline_id):
    update_form = InvoiceAddForm(initial={'quantity': "0"})
    order = Order.objects.get(pk=order_id)
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
                        product_stock = product_stock + order_line.quantity - update_form.cleaned_data['quantity']
                    else:
                        product_stock -= update_form.cleaned_data['quantity'] - order_line.quantity

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
                    messages.success(request, _('Order line updated') + ' ' + _('Quantity') + ' {}'.format(product_stock))

                elif update_form.cleaned_data['quantity'] < order_line.quantity:
                    # Update product stock
                    product_stock += order_line.quantity - update_form.cleaned_data['quantity']
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


def invoice_back_to_draft(request, order_id):
    order = Order.objects.get(pk=order_id)
    if order.shipping_status == 'full':
        messages.warning(request, _('This order is shipped'))

    order.approver = None
    order.approved_date = None
    order.status = 'draft'
    order.save()
    messages.success(request, _('Order status changed to draft'))
    return redirect('staff:invoice_checkout', order.id)


def order_payment_manage(request, order_id):
    order = Order.objects.get(pk=order_id)
    if request.method == 'POST':
        payment_form = OrderPaymentManageForm(request.POST, files=request.FILES, instance=order)
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
def sold_products(request):
    order_lines = OrderLine.objects.all().filter(active=True)
    # order_lines = OrderLine.objects.all().values_list(product.id, flat=True)
    products = dict()
    main_stock = dict()
    # i = 0
    # for line in order_lines:
    #
    #     if line.product.name in products:
    #         # we grab the present value from the products dictionary
    #         quantity = products[line.product.name]['quantity']
    #         vendor = products[line.product.name]['vendor']
    #         stock = products[line.product.name]['stock']
    #
    #         # wether vendor in list is as the same as the vendor in orderline
    #         if vendor == line.purchase.vendor.first_name:
    #             quantity += line.quantity
    #             products[line.product.name] = {
    #                 'quantity': quantity,
    #                 'vendor': vendor,
    #
    #             }
    #         # wether the vendor is diffrent from the vendor in order line
    #         else:
    #             # this line makes a bug and override the availabel book not add a new line
    #             products[line.product.name + str(i)] = {
    #                 'quantity': line.quantity,
    #                 'vendor': line.purchase.vendor.first_name,
    #
    #             }
    #
    #     else:
    #         products[line.product.name] = {
    #             'quantity': line.quantity,
    #
    #         }
    #     i += 1
    for item in order_lines:
        # key = products.get(item.product.id)
        # print(item.product.id)
        if item.product.name in products:
            products[item.product.name] += item.quantity
        else:
            products[item.product.name] = item.quantity
        main_stock[item.product.name] = item.product.stock
    products = sorted(products.items(), key=lambda x: x[1], reverse=True)

    return render(
        request,
        'staff/sold_products.html',
        {'order_lines': order_lines,
         'products': products,
         'main_stock': main_stock,
         }
    )


@staff_member_required
def purchased_products(request):

    purchase_lines = PurchaseLine.objects.all().filter(active=True).order_by('purchase__created')

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
        address_form = VendorAddressAddForm(instance=vendor.default_billing_address)
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
def product_update(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductCreateForm(
            data=request.POST,
            instance=product,
            files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, _('Product updated') +
                             ' {}'.format(product.name))
            return redirect('staff:products')

        else:
            messages.error(request, _('Form is not valid'))
    else:
        form = ProductCreateForm(instance=product)

    return render(
        request,
        'staff/product_create.html',
        {'form': form}

    )


@staff_member_required
def order_shipping(request, order_id):
    form_submit = False
    order = get_object_or_404(Order, pk=order_id)
    shipping_form = OrderShippingForm(instance=order)
    if request.method == 'POST':
        shipping_form = OrderShippingForm(data=request.POST, instance=order)
        if shipping_form.is_valid():
            shipping_form.save()
            # order.status = shipping_form.cleaned_data['shipping_status']
            # order.shipped_code = shipping_form.cleaned_data['shipped_code']
            # order.save()
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
        products = Product.objects.all().filter(available=True).filter(isbn__in=product_isbn).order_by('name')
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
    products = Product.objects.all().filter(available=True).filter(stock__lte=0).order_by('stock')
    return render (
        request,
        'staff/zero_stock_list.html',
        {
            'products': products,
        }
    )
