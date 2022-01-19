from django.shortcuts import render
from django.template.loader import get_template
from django.conf import settings
from django.http import FileResponse



from orders.models import Order, OrderLine




def make_pdf(request, order_id=None):
    order = Order.objects.get(pk=order_id)

    pass
