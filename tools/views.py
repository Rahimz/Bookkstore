from django.shortcuts import render
from django.template.loader import get_template
from django.conf import settings
from django.http import HttpResponse, FileResponse
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from io import BytesIO
from django.db.models import Q
import datetime
from django.core.mail import EmailMessage, mail_admins

import weasyprint
import openpyxl

from orders.models import Order, OrderLine
from zarinpal.models import Payment
from tools.gregory_to_hijry import hij_strf_date, greg_to_hij_date

@staff_member_required
def make_invoice_pdf(request, order_id=None):
    order = Order.objects.get(pk=order_id)

    fa_date = hij_strf_date(greg_to_hij_date(order.created.date()), '%-d %B %Y')

    html = render_to_string('tools/pdf/invoice_pdf.html',
        {'order': order,
        'fa_date': fa_date})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    weasyprint.HTML(string=html).write_pdf(response,
        stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + 'css/invoice_pdf.css')])
    return response

@staff_member_required
def make_invoice_pdf_a4(request, order_id=None):
    order = Order.objects.get(pk=order_id)

    fa_date = hij_strf_date(greg_to_hij_date(order.created.date()), '%-d %B %Y')

    html = render_to_string('tools/pdf/invoice_pdf_a4.html',
        {'order': order,
        'fa_date': fa_date})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    weasyprint.HTML(string=html).write_pdf(response,
        stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + 'css/invoice_pdf_a4.css')])
    return response


def order_export_excel(request, *args, **kwargs):
    orders = Order.objects.filter( Q(status='approved') | Q(paid=True) )

    wb = openpyxl.Workbook()
    sheet = wb.active

    headers = [
        'Order ID', 'Client', 'Client Phone', 'Created', 'Status',
        'billing_address', 'shipping_address', 'shipping_method',  'Created by',
        'Total cost', 'Tota cost after discount', 'discount', 'Payable', 'paid',
        'Customer notes', 'Weight', 'Is gift',
    ]

    for i in range(len(headers)):
        c = sheet.cell(row = 1, column = i + 1 )
        c.value = headers[i]


    for count , order in enumerate(orders):
        title_list = [
            order.id, str(order.client), str(order.client_phone),
            str(order.created,), order.status, order.channel, order.billing_address, order.shipping_address,
            order.shipping_method, str(order.user), order.total_cost, order.total_cost_after_discount, order.discount,
            order.payable, order.paid, order.customer_note, order.weight, order.is_gift,
        ]
        for i in range(len(headers)):
            c = sheet.cell(row = count + 2 , column = i + 1)
            c.value = title_list[i]


    filename = 'media/excel/approved-orders-{}.xlsx'.format(datetime.datetime.now().isoformat(sep='-'))
    wb.save(filename)
    excel = open(filename, 'rb')
    response = FileResponse(excel)


    return response


def draft_order_export_excel(request):
    # TODO: Should mix with order_export_excel
    orders = Order.objects.filter(status='draft')

    wb = openpyxl.Workbook()
    sheet = wb.active

    headers = [
        'Order ID', 'Client', 'Client Phone', 'Created', 'Status', 'Channel',
        'billing_address', 'shipping_address', 'shipping_method',  'Created by',
        'Total cost', 'Tota cost after discount', 'discount', 'Payable', 'paid',
        'Customer notes', 'Weight', 'Is gift',
    ]

    for i in range(len(headers)):
        c = sheet.cell(row = 1, column = i + 1 )
        c.value = headers[i]


    for count , order in enumerate(orders):
        title_list = [ order.id, str(order.client), str(order.client_phone),
             str(order.created,), order.status, order.billing_address, order.shipping_address,
            order.shipping_method, str(order.user), order.total_cost, order.total_cost_after_discount, order.discount,
            order.payable, order.paid, order.customer_note, order.weight, order.is_gift,
        ]
        for i in range(len(headers)):
            c = sheet.cell(row = count + 2 , column = i + 1)
            c.value = title_list[i]


    filename = 'media/excel/draft-orders-{}.xlsx'.format(datetime.datetime.now().isoformat(sep='-'))
    wb.save(filename)
    excel = open(filename, 'rb')
    response = FileResponse(excel)


    return response


def email_to_admin(paymaent_id):
    """
    Function to send email to admin when a payment is done.
    """
    payment = Payment.objects.get(pk=paymaent_id)

    #email body
    subject = 'Successful payment in Ketabedamavand.com {}'.format(payment.id)
    # message = 'A successful payment registered at Zarinpal: \nPayment ID.: {} \nName: {} \nPhone: {} \nAmount: {:,} \n Date & Time:{} \n Ref ID.:{}'.format(
    #     payment.id,
    #     payment.client_name,
    #     payment.client_phone,
    #     payment.amount,
    #     payment.created,
    #     payment.ref_id)
    message = f"A successful payment registered at Zarinpal: \nPayment ID.: {payment.id} \nAmount: {payment.amount:,} \n\nName: {payment.client_name} \nPhone: {payment.client_phone} \n\nDate & Time:{payment.created.isoformat(sep='-')} \n Ref ID.:{payment.ref_id}"

    # send email
    mail_admins(
        subject,
        message,
        fail_silently=False
        )
