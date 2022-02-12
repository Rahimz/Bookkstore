from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


from .models import OrderLine, Purchase, PurchaseLine
from .forms import OrderCreateForm, PurchaseCreateForm, PurchaseLineAddForm, PriceAddForm
from cart.cart import Cart
from discounts.forms import CouponApplyForm
from search.forms import SearchForm
from search.views import ProductSearch
from products.models import Product
from products.price_management import add_price, has_empty_price_row, get_price_index


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
                purchase.payment_date = datetime.now() + timedelta(days=1)
            else:
                purchase.payment_date = datetime.now(
                ) + timedelta(days=purchase_form.cleaned_data['deadline_days'])

            purchase.deadline_days = purchase_form.cleaned_data['deadline_days']
            purchase.save()
            messages.success(request, _('Purchase is created'))
            return redirect('orders:purchase_details', purchase.id)
    else:
        purchase_form = PurchaseCreateForm()

    return render(
        request,
        'staff/purchase/purchase_create.html',
        {'purchase_form': purchase_form}
    )


def purchase_list(request):
    purchases = Purchase.objects.all()

    return render(
        request,
        'staff/purchase/purchase_list.html',
        {'purchases': purchases}
    )


def purchase_details(request, purchase_id, product_id=None, variation='new main'):
    results = None
    variation_list = variation.split()


    search_form = SearchForm()
    purchase = get_object_or_404(Purchase, pk=purchase_id)

    # product_ids = purchase.lines.values_list('id', flat=True)
    # product_ids = [item.product.pk for item in purchase.lines.all()]
    product_ids = [(item.product.pk, item.variation)
                   for item in purchase.lines.all()]

    product = get_object_or_404(Product, pk=product_id) if product_id else None

    if product:
        # variation_dict = {
        #     'main': {
        #         'price': product.price,
        #         'stock': product.stock,
        #     },
        #     'v1': {
        #         'price': product.price_1,
        #         'stock': product.stock_1,
        #     },
        #     'used': {
        #         'price': product.price_used,
        #         'stock': product.stock_used, }
        # }
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
            },
            'used': {
                'main': {
                    'price': product.price_used,
                    'stock': product.stock_used
                },
            }
        }

        price = variation_dict[variation_list[0]][variation_list[1]]['price']
        price = variation_dict[variation_list[0]][variation_list[1]]['stock']

        if (product.id, variation) in product_ids:
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
            'results': results
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
            product.stock += item.quantity
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

    if request.method == 'POST':
        price_form = PriceAddForm(data=request.POST)
        if price_form.is_valid():
            new_price = price_form.cleaned_data['price']
            new_variation = price_form.cleaned_data['variation'] #'new' , 'used'
            quantity = price_form.cleaned_data['quantity']
            if has_empty_price_row(product=product, variation=new_variation):


                add_price(
                    product_id=product.id,
                    variation=new_variation,
                    price=new_price,
                    stock=quantity)

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
