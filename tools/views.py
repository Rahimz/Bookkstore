from django.shortcuts import render
import io
from django.http import FileResponse

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import cm

from orders.models import Order, OrderLine

def make_pdf(request, order_id):
    order = Order.objects.get(pk=order_id)

    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer,pagesize=A4, bottomup=0)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawCentredString(10*cm, 1*cm, order.token)
    dist = 2
    for item in order.lines.all():
        p.drawCentredString(15*cm, dist*cm, item.product.name)
        p.drawCentredString(10*cm, dist*cm, str(item.quantity))
        p.drawCentredString(5*cm, dist*cm, str(item.get_cost_after_discount()))

        dist +=1
    # p.drawString(5*cm, 5*cm, "Hello world. 5,5")
    #
    # p.drawString(10*cm, 5*cm, "Hello world. 10,5")
    # p.drawString(10*cm, 10*cm, "Hello world. 10,10")
    # p.drawString(10*cm, 20*cm, "Hello world. 10,20")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='hello.pdf')
