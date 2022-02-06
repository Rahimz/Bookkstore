from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


from .models import OrderLine, Purchase
from .forms import OrderCreateForm, PurchaseCreateForm
from cart.cart import Cart
from discounts.forms import CouponApplyForm


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
            if not purchase_form.cleaned_data['payment_days']:
                purchase.payment_date = datetime.now() + timedelta(days=1)
            else:
                purchase.payment_date = datetime.now() + timedelta(days=purchase_form.cleaned_data['payment_days'])

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


def purchase_details(request, purchase_id):
    purchase = get_object_or_404(Purchase, pk=purchase_id)
    return render(
        request,
        'staff/purchase/purchase_details.html',
        {'purchase': purchase}
    )
