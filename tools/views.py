from django.shortcuts import render
from django.template.loader import get_template
from django.conf import settings
from django.http import FileResponse

import pdfkit

from orders.models import Order, OrderLine




def make_pdf(request, order_id=None):
    order = Order.objects.get(pk=order_id)

    # template = get_template("staff/invoice_create.html")
    # context = {'order': order}
    # html = template.render(context)
    html = "<html><body><p>Hello world</p></body></html>"
    string_sample = "Hello world"
    pdf = pdfkit.from_string(string_sample, "output.pdf", configuration=settings.WKHTMLTOPDF_CMD)

    response = HttpResponse(pdf, content_type='application/pdf')

    response['Content-Disposition'] = 'attachment; filename=output.pdf'

    return response
