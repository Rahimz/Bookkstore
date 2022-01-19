from django.shortcuts import render
from django.template.loader import get_template
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required

import weasyprint

from orders.models import Order, OrderLine


@staff_member_required
def make_invoice_pdf(request, order_id=None):
    order = Order.objects.get(pk=order_id)

    html = render_to_string('tools/pdf/invoice_pdf.html',
        {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    weasyprint.HTML(string=html).write_pdf(response,
        stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + 'css/invoice_pdf.css')])
    return response
