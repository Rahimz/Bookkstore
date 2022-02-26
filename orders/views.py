from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from math import trunc
from decimal import Decimal


from .models import OrderLine, Purchase, PurchaseLine
from .forms import OrderCreateForm, PurchaseCreateForm, PurchaseLineAddForm, PriceAddForm, PurchaseLineUpdateForm
from cart.cart import Cart
from discounts.forms import CouponApplyForm
from search.forms import SearchForm
from search.views import ProductSearch
from products.models import Product
from products.price_management import add_price, has_empty_price_row, get_price_index, sort_price
from tools.fa_to_en_num import number_converter


@login_required
def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()
            for item in cart:
                OrderLine.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            # clear the cart
            cart.clear()
            # launch asynchronous task
            # order_created.delay(order.id)
            # set the order in the session
            request.session['order_id'] = order.id
            # redirect for payment
            # return redirect(reverse('zarinpal:request'))
            return render(request,
                          'orders/created.html',
                          {'order': order})
    else:
        # try:
        #     address = Address.objects.get(user=request.user, fav_address=True)
        #     if address:
        #         data_initial = {
        #         'first_name' : address.first_name,
        #         'last_name' : address.last_name,
        #         'phone' : address.phone,
        #         'address' : address.address,
        #         'postal_code' : address.postal_code,
        #         'city' : address.city}
        #         form = OrderCreateForm(data_initial)
        # except:
        #     form = OrderCreateForm()
        form = OrderCreateForm()
    return render(request,
                  'orders/create.html',
                  {'cart': cart, 'form': form})


def purchase_create(request):
    if request.method == 'POST':
        purchase_form = PurchaseCreateForm(data=request.POST)
        if purchase_form.is_valid():
            purchase = purchase_form.save(commit=False)
            purchase.registrar = request.user
            if not purchase_form.cleaned_data['deadline_days']:
                purchase.payment_date = datetime.now() + timedelta(days=2)
            else:
                purchase.payment_date = datetime.now(
                ) + timedelta(days=purchase_form.cleaned_data['deadline_days'])

            purchase.deadline_days = purchase_form.cleaned_data['deadline_days']

            purchase_form.save
            purchase.save()
            messages.success(request, _('Purchase is created'))
            return redirect('orders:purchase_details', purchase.id)
    else:
        purchase_form = PurchaseCreateForm(initial={'deadline_days': 10})

    return render(
        request,
        'staff/purchase/purchase_create.html',
        {'purchase_form': purchase_form}
    )


def purchase_list(request):
    purchases = Purchase.objects.all().filter(active=True)

    return render(
        request,
        'staff/purchase/purchase_list.html',
        {'purchases': purchases}
    )


def purchase_details(request, purchase_id, product_id=None, variation='new main'):
    results = None

    search_form = SearchForm()
    purchase = get_object_or_404(Purchase, pk=purchase_id)

    purchase_lines = purchase.lines.all()

    # product_ids = purchase.lines.values_list('id', flat=True)
    # product_ids = [item.product.pk for item in purchase.lines.all()]
    product_ids = [(item.product.pk, item.variation, item.price)
                   for item in purchase_lines]

    product = get_object_or_404(Product, pk=product_id) if product_id else None

    if product:

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

        price = variation_dict[variation_list[0]][variation_list[1]]['price']
        stock = variation_dict[variation_list[0]][variation_list[1]]['stock']

        if (product.id, variation, price) in product_ids:
            purchase_line = PurchaseLine.objects.get(
                purchase=purchase, product=product, variation=variation)
            purchase_line.quantity += 1
            purchase_line.save()
            purchase.save()

            messages.success(request, _('Purchase row updated'))
            return redirect('orders:purchase_details', purchase.id)
        else:
            PurchaseLine.objects.create(
                purchase=purchase,
                product=product,
                price=price,
                quantity=1,
                variation=variation,
                discount=price * purchase.vendor.overal_discount / 100,
            )

            purchase.save()

            messages.success(request, _('Purchase row added'))
            return redirect('orders:purchase_details', purchase.id)

    if request.method == 'POST':
        line_form = PurchaseLineAddForm(data=request.POST)
        search_form = SearchForm(data=request.POST)
        if search_form.is_valid():
            search_query = search_form.cleaned_data['query']
            search_query= number_converter(search_query)
            results = ProductSearch(
                object=Product, query=search_query).order_by('name', 'publisher')

        # if line_form.is_valid():
        #     new_line = line_form.save(commit=False)
        #     new_line.purchase = purchase
        #     product = new_line.product
        #     new_line.save()
        #
        #     product.stock += new_line.quantity
        #     product.save()
        #
        #     messages.success(request, _('Purchase row added') + str(product.id))
        #     return redirect('orders:purchase_details' , purchase.id)
    else:
        line_form = PurchaseLineAddForm()
        search_form = SearchForm()

    return render(
        request,
        'staff/purchase/purchase_details.html',
        {
            'purchase': purchase,
            'line_form': line_form,
            'search_form': search_form,
            'results': results,
            'purchase_lines': purchase_lines,
        }
    )


def purchase_update(request, purchase_id):
    purchase = get_object_or_404(Purchase, pk=purchase_id)
    purchase_form = PurchaseCreateForm(instance=purchase)
    if request.method == 'POST':
        purchase_form = PurchaseCreateForm(
            data=request.POST, instance=purchase)
        if purchase_form.is_valid():
            purchase = purchase_form.save(commit=False)
            purchase.registrar = request.user
            purchase.payment_date = datetime.now(
            ) + timedelta(days=purchase_form.cleaned_data['deadline_days'])

            purchase.save()

            messages.success(request, _('Purchase is updated'))
            return redirect('orders:purchase_details', purchase.id)

    else:
        purchase_form = PurchaseCreateForm(instance=purchase)

    return render(
        request,
        'staff/purchase/purchase_create.html',
        {'purchase_form': purchase_form}
    )


def purchase_checkout(request, purchase_id):
    purchase = get_object_or_404(Purchase, pk=purchase_id)

    product_ids = [item.product.pk for item in purchase.lines.all()]
    if purchase.status == 'draft':

        # TODO: we should check which stock should be updated
        # if variation[0] == 'new':
        #     if variation[1] == 'main':
        #         product.stock = stock
        #     elif variation[1] == 'v1':
        #         product.stock_1 = stock
        # elif variation[0] == 'used':
        #     if variation[1] == 'main':
        #         product.stock_used = stock

        for item in purchase.lines.all():
            product = item.product
            # we have some old row in purchase lines
            if item.variation in ('main', 'new main'):
                product.stock += item.quantity

            # we have some old row in purchase lines
            elif item.variation in ('v1', 'new v1'):
                product.stock_1 += item.quantity

            elif item.variation == 'new v2':
                product.stock_2 += item.quantity

            elif item.variation == 'new v3':
                product.stock_3 += item.quantity

            elif item.variation == 'new v3':
                product.stock_4 += item.quantity

            elif item.variation == 'new v4':
                product.stock_5 += item.quantity

            # we have some old row in purchase lines
            elif item.variation in ('used', 'used main'):
                product.stock_used += item.quantity

            product.vendor = purchase.vendor
            product.vendors.add(purchase.vendor)
            # messages.success(request, _('Vendor added to product vendors'))
            product.save()

        purchase.approver = request.user
        purchase.approved_date = datetime.now()
        purchase.status = 'approved'
        purchase.save()
        messages.success(request, _('Purchase added to stock'))
    else:
        messages.error(request, _('This purchase is already approved'))

    return render(
        request,
        'staff/purchase/purchase_checkout.html',
        {'purchase': purchase}
    )


def price_management(request, product_id, purchase_id):
    product = get_object_or_404(Product, pk=product_id)
    purchase = get_object_or_404(Purchase, pk=purchase_id)
    new_prices = [product.price, product.price_1, product.price_2,
                  product.price_3, product.price_4, product.price_5, ]
    if request.method == 'POST':
        price_form = PriceAddForm(data=request.POST)
        if price_form.is_valid():
            new_price = price_form.cleaned_data['price']
            # 'new' , 'used'
            new_variation = price_form.cleaned_data['variation']
            # quantity = price_form.cleaned_data['quantity']
            if new_price in new_prices:
                messages.error(request, _(
                    'There is an equal price in the list'))
                return redirect('orders:price_management', product_id=product.id, purchase_id=purchase.id)

            if has_empty_price_row(product=product, variation=new_variation) and not (new_price in new_prices):

                add_price(
                    product_id=product.id,
                    variation=new_variation,
                    price=new_price,
                    stock=0)

                messages.success(request, _('Price added'))
                # return redirect('orders:price_management', product_id=product.id , purchase_id=purchase.id)
                get_variation = get_price_index(
                    product_id=product.id, variation=new_variation, price=new_price)
                # messages.success(request, f"{new_variation} {get_variation}")
                # return redirect('orders:price_management', purchase_id=purchase.id, product_id=product.id)
                return redirect('orders:purchase_add_line_v', purchase_id=purchase.id, product_id=product.id, variation=f"{new_variation} {get_variation}")

            else:
                messages.error(request, _(
                    'There is not empty price row for this product variation'))

    else:
        price_form = PriceAddForm()
    return render(
        request,
        'staff/price_management.html',
        {
            'product': product,
            'price_form': price_form,
            'purchase': purchase,
        }
    )



def price_remove(request,purchase_id, product_id, variation):
    product = Product.objects.get(pk=product_id)
    purchase = Purchase.objects.get(pk=purchase_id)


    if variation in ('main', 'new main'):
        product.price = 0

    # we have some old row in purchase lines
    elif variation in ('v1', 'new v1'):
        product.price_1 = 0

    elif variation == 'new v2':
        product.price_2 = 0
        print('here v2')

    elif variation == 'new v3':
        product.price_3 = 0

    elif variation == 'new v3':
        product.price_4 = 0

    elif variation == 'new v4':
        product.price_5 = 0

    # we have some old row in purchase lines
    elif variation in ('used', 'used main'):
        product.price_used = 0

    product.save()
    sort_price(product)

    messages.success(request, _('The price removed'))
    return redirect('orders:price_management', purchase.id, product.id)



def purchase_line_add(request, product_id, purchase_id, variation, purchaseline_id=None):
    purchase = get_object_or_404(Purchase, pk=purchase_id)

    product = get_object_or_404(Product, pk=product_id)
    product_ids = [(item.product.pk, item.variation, item.price)
                   for item in purchase.lines.all()]

    if purchaseline_id:
        purchaseline = get_object_or_404(PurchaseLine, pk=purchaseline_id)

    if variation == 'main':
        variation = 'new main'
    elif variation == 'v1':
        variation = 'new v1'
    elif variation == 'used':
        variation = 'used main'
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

    price = variation_dict[variation_list[0]][variation_list[1]]['price']
    stock = variation_dict[variation_list[0]][variation_list[1]]['stock']

    if request.method == 'POST':
        if purchaseline_id:
            purchase_update_form = PurchaseLineUpdateForm(data=request.POST, instance=purchaseline)
        else:
            purchase_update_form = PurchaseLineUpdateForm(data=request.POST)

        if purchase_update_form.is_valid():
            # discount calculator
            new_form = purchase_update_form.save(commit=False)

            discount = new_form.discount
            discount_percent = new_form.discount_percent
            quantity = new_form.quantity


            if (product.id, variation, price) in product_ids:
                purchase_line = PurchaseLine.objects.get(
                    purchase=purchase, product=product, variation=variation)
                purchase_line.quantity = quantity
                purchase_line.discount = discount
                purchase_line.discount_percent = discount_percent
                purchase_line.save()
                purchase.save()

                messages.success(request, _('Purchase row updated'))
                return redirect('orders:purchase_details', purchase.id)
            else:
                print(discount , discount_percent)
                PurchaseLine.objects.create(
                    purchase=purchase,
                    product=product,
                    price=price,
                    quantity=quantity,
                    variation=variation,
                    discount=discount,
                    discount_percent=discount_percent
                )

                purchase.save()

                messages.success(request, _('Purchase row added'))
                return redirect('orders:purchase_details', purchase.id)
            # messages.success(request, _('Purchaseline updated'))
    else:
        if purchaseline_id:
            purchase_update_form = PurchaseLineUpdateForm(instance=purchaseline)
        else:
            purchase_update_form = PurchaseLineUpdateForm()
    return render(
        request,
        'staff/purchase/purchaseline_add.html',
        {
            'purchase_update_form': purchase_update_form,
            'purchase': purchase,
            'product': product,
            'price': price,
            'stock': stock,
            'purchaseline_id': purchaseline_id
        }
    )


def purchaseline_remove(request, purchaseline_id):
    purchaseline = get_object_or_404(PurchaseLine, pk=purchaseline_id)
    purchase_id = purchaseline.purchase.id
    purchaseline.delete()
    messages.success(request, _('Purchaseline row removed'))
    return redirect('orders:purchase_details', purchase_id)
