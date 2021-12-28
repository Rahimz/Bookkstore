from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from products.models import Product
from .cart import Cart
from .forms import CartAddProductForm
# from coupons.forms import CouponApplyForm
# from shop.recommender import Recommender


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        quantity = cd['quantity']
        if product.stock >= quantity:
            cart.add(product=product,
                     quantity=cd['quantity'],
                     override_quantity=cd['override'])
            product.stock -= quantity
            product.save()
            messages.success(request, _('Product added to cart!'))
        else:
            messages.warning(request, _(
                'There are not enough products in stock!'))
            return redirect('shop/product_detail', id=product_id, slug=product.slug)
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    # this loop make a edit field form for each item in cart
    # it sets override True to use cart add method to update it
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
                                            initial={
                                                'quantity': item['quantity'],
                                                'override': True
                                            })
    # coupon_apply_form = CouponApplyForm()

    # r = Recommender()
    cart_products = [item['product'] for item in cart]
    # recommended_products = r.suggest_products_for(cart_products,
    # max_results=4)
    return render(
        request,
        'cart/detail.html',
        {'cart': cart,
         # 'coupon_apply_form': coupon_apply_form,
         # 'recommended_products': recommended_products
         })
