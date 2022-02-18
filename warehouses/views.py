from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

from .forms import RefundClientForm
from .models import Refund
from orders.models import Order
from account.models import CustomUser
from products.models import Product


def refund_from_client(request):
    order = None
    product = None
    client = None
    refund_form = RefundClientForm()
    if request.method == 'POST':
        refund_form = RefundClientForm(data=request.POST)
        if refund_form.is_valid():
            try:
                order = get_object_or_404(Order, pk=refund_form.cleaned_data['order_id'])
            except:
                messages.error(request, _('Order is not valid') )

            try:
                product = get_object_or_404(Product, isbn=refund_form.cleaned_data['product_isbn'])
            except:
                messages.error(request, _('Product is not valid'))

            try:
                client = get_object_or_404(CustomUser, phone=refund_form.cleaned_data['client_phone'])
            except:
                messages.error(request, _('Client is not valid'))

            if order and product and client:
                Refund.objects.create(
                    order=order,
                    product=product,
                    price=refund_form.cleaned_data['price'],
                    quantity=refund_form.cleaned_data['quantity'],
                    from_client=client,
                    registrar=request.user,
                )
                messages.success(request, _('Refund order registered'))
                return redirect('staff:warehouse')
    else:
        refund_form = RefundClientForm()
    return render(
        request,
        'staff/refund_from_client.html',
        {
            'refund_form': refund_form,
        }
    )


def refund_list_client(request):
    refunds = Refund.objects.all().filter(from_client__isnull=False)
    return render(
        request,
        'staff/refund_list_client.html',
        {
        'refunds':refunds
        }
    )
