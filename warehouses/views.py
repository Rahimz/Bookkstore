from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum

from .forms import RefundClientForm
from .models import Refund
from orders.models import Order, OrderLine, PurchaseLine
from account.models import CustomUser, Credit
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
                try:
                    client.credit.balance += refund_form.cleaned_data['price']
                    messages.success(request, _('Client credit balance updated'))
                    client.credit.save()
                    return redirect('staff:refund_list_client')
                except:
                    Credit.objects.create(
                        user=client,
                        balance=refund_form.cleaned_data['price']
                    )
                    messages.success(request, _('Credit added to client balance'))
                    return redirect('staff:refund_list_client')

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
    refunds = Refund.objects.all().filter(from_client__isnull=False).filter(active=True)
    return render(
        request,
        'staff/refund_list_client.html',
        {
        'refunds':refunds
        }
    )


@staff_member_required
def product_workflow(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    product_sales = OrderLine.objects.filter(active=True).filter(product=product).order_by('pk')
    sales = OrderLine.objects.filter(active=True).filter(product=product).aggregate(quantity=Sum('quantity'))

    product_purchases = PurchaseLine.objects.filter(active=True).filter(product=product).order_by('pk')
    purchases = PurchaseLine.objects.filter(active=True).filter(product=product).aggregate(quantity=Sum('quantity'))

    # order_0_day = Order.objects.filter(active=True).filter(created__date=(datetime.now().date())).aggregate(total_sales=Sum('payable'), total_quantity=Sum('quantity'))
    return render(
        request,
        'warehouses/product_workflow.html',
        {
            'product': product,
            'product_sales': product_sales,
            'sales': sales,
            'product_purchases': product_purchases,
            'purchases': purchases,
        }
    )
