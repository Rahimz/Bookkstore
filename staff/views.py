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

from .forms import ProductCreateForm, OrderCreateForm, InvoiceAddForm, CategoryCreateForm, OrderShippingForm
from products.models import Product, Category
from orders.models import Order, OrderLine, PurchaseLine
from orders.forms import OrderAdminCheckoutForm
from search.forms import ClientSearchForm, BookIsbnSearchForm, SearchForm
from search.views import ProductSearch
from account.models import CustomUser, Vendor, Address
from account.forms import VendorAddForm, AddressAddForm
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
    if channel=='all' and period == 'all':
        orders = Order.objects.filter(
            Q(status='approved') | Q(paid=True))

    # 'mix' channel means we need the orders that should be collected
    if channel == 'mix' and period=='all':
        # orders = Order.objects.filter(
        #     Q(status='approved') | Q(paid=True)).exclude(channel='cashier')
        orders = Order.objects.exclude(channel='cashier').exclude(status='draft')

    # staff/orders/30/mix
    elif channel == 'mix' and period not in ('all', 'mix'):
        orders = Order.objects.filter(
            Q(status='approved') | Q(paid=True)).exclude(channel='cashier').filter(approved_date__gte=datetime.now() - timedelta(int(period)))

    # staff/orders/365/cashier
    elif channel == 'cashier' and period not in ('all', 'mix'):
        orders = Order.objects.filter(
            Q(status='approved') | Q(paid=True)).filter(channel='cashier').filter(approved_date__gte=datetime.now() - timedelta(int(period)))

    else:
        orders = Order.objects.filter(
            Q(status='approved') | Q(paid=True))

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
    products_object = Product.objects.all()

    search_form = SearchForm()
    if request.method == 'POST':
        search_form = SearchForm(data=request.POST)
        if search_form.is_valid():
            search_query = search_form.cleaned_data['query']

            products_object = ProductSearch(object=Product, query=search_query).order_by('name', 'publisher')

    # pagination
    paginator = Paginator(products_object, 50) # 50 posts in each page
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
        'products':products,
        'page': page,
        'search_form': search_form,
        }
    )


@staff_member_required
def product_create(request):
    if request.method == 'POST':
        form = ProductCreateForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.category = Category.objects.get(name=form.cleaned_data['category'])

            product.save()
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
        {'form': form }
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
        {'form': form }
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
def invoice_create(request, order_id=None, book_id=None, variation='main'):
    books = None
    results = None
    book = None
    # isbn = ''
    search_form = SearchForm()
    update_form = InvoiceAddForm()
    book_ids = []
    update_forms = {}
    if order_id:
        order = Order.objects.get(pk=order_id)
        book_ids = [(item.product.pk, item.variation) for item in order.lines.all()]

        # TODO: The loop should be replaced with a query to enhance the performance
        for item in order.lines.all():
            # update_forms[item.id]
            form  = InvoiceAddForm()
            update_forms[item.id] = form

    else:
        order = None

    if book_id:
        book = Product.objects.get(pk=book_id)

        # in this dict we handle the other prices and quantities variations
        variation_dict = {
            'main': {
                'price': book.price,
                'stock': book.stock,
            },
            'v1': {
                'price': book.price_1,
                'stock': book.stock_1,
            },
            'used': {
                'price': book.price_used,
                'stock': book.stock_used,}
        }
        price = variation_dict[variation]['price']
        stock = variation_dict[variation]['stock']

    isbn_search_form = BookIsbnSearchForm()



    # If the search result contains more than one results
    #  we handle it in these if statement
    if order_id and book_id:

        # Check the stock of product
        if stock <= 0:
            messages.error(request, _('Not enough stock!'))
            return redirect('staff:invoice_create', order_id)

        # add book to invoice
        if (book.id, variation) in book_ids:
            order_line = OrderLine.objects.get(order=order, product=book, variation=variation)
            order_line.quantity += 1
            order_line.save()
            order.save()
        else:
            order_line = OrderLine.objects.create(
                order = order,
                product = book,
                quantity = 1,
                price = price,
                variation = variation,
            )
            order.save()

            # Update product stock
            stock -= 1

            if variation == 'main':
                book.stock = stock
            elif variation  == 'v1':
                book.stock_1 = stock
            elif variation == 'used':
                book.stock_used = stock

            book.save()
        messages.success(request, _('Product is added to invoice'))

        return redirect('staff:invoice_create', order.id)

    # When we add a book for first time and we dont have an order
    if (not order_id) and book_id:
        if stock <= 0:
            messages.error(request, _('Not enough stock!'))
            return redirect('staff:invoice_create')

        # if book.stock >=1:
        order = Order.objects.create(
                    user = request.user,
                    status = 'draft',
                    shipping_method = 'pickup',
                )
        messages.success(request, _('Order is created') + ' : {}'.format(order.id))
        order_line = OrderLine.objects.create(
            order = order,
            product = book,
            quantity = 1,
            price = price,
            variation = variation,
        )
        order.save()
        # Update product stock
        stock -= 1

        if variation == 'main':
            book.stock = stock
        elif variation  == 'v1':
            book.stock_1 = stock
        elif variation == 'used':
            book.stock_used = stock

        book.save()

        messages.success(request,  _('Product is added to invoice'))
        return redirect('staff:invoice_create', order.id)


    # ::# TODO: should refactor shome of the codes does not use
    if request.method == 'POST':
        isbn_search_form =BookIsbnSearchForm(data=request.POST)
        search_form = SearchForm(data=request.POST)
        if search_form.is_valid():
            search_query = search_form.cleaned_data['query']

            # Here we grab the quey search from database and
            # search the fields: name, author, translator, publisher, isbn
            results = ProductSearch(object=Product, query=search_query).order_by('name', 'publisher')

            # if the results has only one item, the item automaticaly added to invoice
            if len(results) == 1:
                book = results.first()
                # Check the stock of product
                if book.has_other_prices:
                    messages.warning(request, _('This book has other prices'))
                    # if not order:
                    #     return redirect('staff:invoice_create')
                    # if order:
                    #     return redirect('staff:invoice_create', order.id)
                elif not book.has_other_prices:
                    if book.stock <= 0:
                        messages.error(request, _('Not enough stock!'))
                        if not order:
                            return redirect('staff:invoice_create')
                        if order:
                            return redirect('staff:invoice_create', order.id)
                    # if the order has not created yet, we created it here
                    if not order:
                        order = Order.objects.create(
                                    user = request.user,
                                    status = 'draft',
                                    shipping_method = 'pickup',
                                )
                        messages.success(request,  _('Order is created') + ' : {}'.format(order.id))

                    # if the book is added in the invoice we will update the quantity in invoice
                    if (book.pk, 'main') in book_ids and not book.has_other_prices:
                        order_line = OrderLine.objects.get(order=order, product=book)
                        order_line.quantity += 1
                        order_line.variation = 'main'
                        order_line.save()
                        order.save()

                        # Update product stock
                        book.stock -=1
                        book.save()

                    # if the book is not in invoice we will create an invoice orderline
                    else:
                        order_line = OrderLine.objects.create(
                            order = order,
                            product = book,
                            quantity = 1,
                            price = book.price,
                            variation = 'main'
                        )
                        order.save()

                        book.stock -= 1
                        book.save()
                    messages.success(request, _('Product is added to invoice'))
        else:
            pass

    search_form = SearchForm()
    return render(
        request,
        'staff/invoice_create.html',
        {'order': order,
         'isbn_search_form': isbn_search_form,
         # 'isbn': isbn,
         'book_ids': book_ids,
         'update_form': update_form,
         'search_form': search_form,
         'results': results,

    })


@staff_member_required
def invoice_checkout(request, order_id, client_id=None):
    order = Order.objects.get(pk=order_id)
    checkout_form = OrderAdminCheckoutForm(instance=order)
    client_search_form = ClientSearchForm()
    client = CustomUser.objects.get(pk=client_id) if client_id else None
    clients = None
    if request.method == 'POST':
        checkout_form = OrderAdminCheckoutForm(data=request.POST, instance=order)
        client_search_form = ClientSearchForm(data=request.POST)
        if client_search_form.is_valid():
            # messages.debug(request, 'client_search_form.is_valid')
            query = client_search_form.cleaned_data['query']

            #we will check if any farsi character is in the query we will changed it
            query = number_converter(query)
            clients = CustomUser.objects.filter(is_client=True).order_by('-pk').exclude(is_superuser=True).exclude(username='guest')
            clients = clients.annotate(
                search=SearchVector('first_name', 'last_name', 'username', 'phone'),).filter(search__contains=query)
            # try:
            #     client = CustomUser.objects.get(phone=query, is_client=True)
            # except:
            #     pass
            #
            # if client:
            #     messages.success(request, _('Client found'))
            #
            # elif query and not client:
            #     client = CustomUser(
            #         phone=query,
            #         username=query,
            #         email="{}@ketabedamavand.com".format(query)
            #     )
            #     client.save()
            #     messages.success(request, _('Client added')+ ' {}'.format(client.phone))
            #
            # elif not client:
            #     client = CustomUser.objects.get(username='guest')

        if checkout_form.is_valid():
            if not client:
                client = CustomUser.objects.get(username='guest')
            order.client = client
            order.paid = checkout_form.cleaned_data['paid']
            order.customer_note = checkout_form.cleaned_data['customer_note']
            order.is_gift = checkout_form.cleaned_data['is_gift']
            order.channel = checkout_form.cleaned_data['channel']
            order.discount = checkout_form.cleaned_data['discount']
            order.status = 'approved'
            order.approver = request.user
            order.approved_date = datetime.now()
            if order.channel == 'cashier':
                order.shipping_method = 'pickup'
                order.shipping_status = 'full'
            else:
                order.shipping_method = 'post'
            order.save()
            messages.success(request, _('Order approved'))
            return redirect('staff:order_list', period='all', channel='all')
    return render(
        request,
        'staff/invoice_checkout.html',
        {'client_search_form': client_search_form,
         'order': order,
         'checkout_form': checkout_form,
         'clients': clients,
         'client': client,
    })


@staff_member_required
def orderline_update(request, order_id, orderline_id):
    update_form = InvoiceAddForm(initial={'quantity':"0"})
    order = Order.objects.get(pk=order_id)
    if request.method == 'POST':
        update_form = InvoiceAddForm(data=request.POST)
        if update_form.is_valid():
            order_line = OrderLine.objects.get(pk=orderline_id)
            product = order_line.product
            variation = order_line.variation

            variation_dict = {
                'main': {
                    'price': product.price,
                    'stock': product.stock,
                },
                'v1': {
                    'price': product.price_1,
                    'stock': product.stock_1,
                },
                'used': {
                    'price': product.price_used,
                    'stock': product.stock_used,}
            }
            product_price = variation_dict[order_line.variation]['price']
            product_stock = variation_dict[order_line.variation]['stock']

            if update_form.cleaned_data['remove'] == True:
                """
                remove an orde line if remove checkbox is clicked
                """
                # Update product stock
                product_stock += order_line.quantity

                if variation == 'main':
                    product.stock = product_stock
                elif variation  == 'v1':
                    product.stock_1 = product_stock
                elif variation == 'used':
                    product.stock_used = product_stock

                product.save()

                order_line.delete()
                order.save()
                return redirect('staff:invoice_create', order.id)

            if update_form.cleaned_data['quantity'] != 0:
                if update_form.cleaned_data['quantity'] > order_line.quantity:
                    if update_form.cleaned_data['quantity'] > order_line.quantity + product_stock:
                        messages.error(request, _('Not enough stock') + ' ' + _('Quantity') + ' {}'.format(product_stock))
                        return redirect('staff:invoice_create', order.id)
                    else:
                        # Update product stock
                        product_stock -= update_form.cleaned_data['quantity'] - order_line.quantity

                        if variation == 'main':
                            product.stock = product_stock
                        elif variation  == 'v1':
                            product.stock_1 = product_stock
                        elif variation == 'used':
                            product.stock_used = product_stock

                        product.save()


                elif update_form.cleaned_data['quantity'] < order_line.quantity:
                    # Update product stock
                    product_stock += order_line.quantity - update_form.cleaned_data['quantity']

                    if variation == 'main':
                        product.stock = product_stock
                    elif variation  == 'v1':
                        product.stock_1 = product_stock
                    elif variation == 'used':
                        product.stock_used = product_stock
                    product.save()

                order_line.quantity = update_form.cleaned_data['quantity']
                order_line.save()
                order.save()


            if update_form.cleaned_data['discount'] != 0:
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
    draft_orders = Order.objects.filter(status='draft')

    return render(
        request,
        'staff/draft_orders.html',
        {'draft_orders': draft_orders}
    )


@staff_member_required
def category_list(request):
    main_categories = Category.objects.filter(active=True, parent_category=None)

    return render(
        request,
        'staff/categories.html',
        {'main_categories': main_categories }
    )


@staff_member_required
def sold_products(request):
    order_lines = OrderLine.objects.all()
    # order_lines = OrderLine.objects.all().values_list(product.id, flat=True)
    products = dict()
    for item in order_lines:
        # key = products.get(item.product.id)
        # print(item.product.id)
        if  item.product.name in products:
            products[item.product.name] += item.quantity
        else:
            products[item.product.name] = item.quantity
    products = sorted(products.items(), key=lambda x: x[1], reverse=True)

    return render(
        request,
        'staff/sold_products.html',
        {'order_lines': order_lines,
        'products':products,
        }
    )


@staff_member_required
def purchased_products(request):

    purchase_lines = PurchaseLine.objects.all().order_by('purchase__created')


    # order_lines = OrderLine.objects.all().values_list(product.id, flat=True)
    products = dict()
    i= 0
    for line in purchase_lines:


        if  line.product.name in products:
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
        'products':products,
        # 'test': test,
        }
    )


@staff_member_required
def vendor_add(request):
    vendor_form = VendorAddForm()
    address_form = AddressAddForm(initial={'country':'IR', 'city':_('Tehran')})
    if request.method == 'POST':
        vendor_form = VendorAddForm(request.POST)
        address_form = AddressAddForm(request.POST)
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

            messages.success(request, _('Vendor is added!') + ' {}'.format(vendor.first_name))

            return HttpResponseRedirect(reverse('staff:vendor_list'))
        else:
            messages.error(request, _('Form is not valid'))
    else:
        vendor_form = VendorAddForm()
        address_form = AddressAddForm(initial={'country':'IR', 'city':_('Tehran')})
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
        address_form = AddressAddForm(request.POST, instance=vendor.default_billing_address)
        if vendor_form.is_valid() and address_form.is_valid():
            vendor_form.save()
            address_form.save()
            messages.success(request, _('Vendor is updated') + ': {}'.format(vendor.first_name))
        else:
            messages.error(request, _('Form is not valid'))
    else:
        vendor_form = VendorAddForm(instance=vendor)
        address_form = AddressAddForm(instance=vendor.default_billing_address)
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
            messages.success(request, _('Product updated') + ' {}'.format(product.name))
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
            messages.success(request, 'Shipping status is updated' )
            messages.warning(request, 'Update the order list' )
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
    orders = Order.objects.all().exclude(channel='cashier').filter(Q(status='approved') | Q(status='paid'))

    countries = set(list(filter(None, Address.objects.all().values_list('country', flat=True))))


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
