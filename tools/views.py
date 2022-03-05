from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import get_template
from django.conf import settings
from django.http import HttpResponse, FileResponse
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from io import BytesIO
from django.db.models import Q
import datetime
from django.core.mail import EmailMessage, mail_admins, mail_managers, get_connection
import random
from django.core.files.base import ContentFile
from django.core.files import File

import weasyprint
import openpyxl
from openpyxl.styles import Color, Fill
import qrcode
import qrcode.image.svg

from orders.models import Order, OrderLine
from zarinpal.models import Payment
from tools.gregory_to_hijry import hij_strf_date, greg_to_hij_date
from shop.models import Slogan
from account.models import CustomUser
from products.models import Product

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
def print_invoice(request, order_id=None):
    order = Order.objects.get(pk=order_id)
    slogan_id = random.choice(Slogan.objects.values_list('pk', flat=True))
    slogan = Slogan.objects.get(pk=slogan_id)
    fa_date = hij_strf_date(greg_to_hij_date(order.created.date()), '%-d %B %Y')

    return render(
        request,
        'tools/pdf/print_invoice.html',
        {
            'order': order,
            'fa_date': fa_date,
            'slogan': slogan,
        }
    )


@staff_member_required
def print_address(request, client_id, kind='billing'):
    client = CustomUser.objects.get(pk=client_id)

    return render(
        request,
        'tools/pdf/print_address.html',
        {
            'client': client,
            'kind': kind
        }
    )


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


def order_export_excel(request, criteria):
    # TODO: we handle all order export with one function but we should add parameter to
    # handle differnt kind of report
    orders = Order.objects.filter(status=criteria).filter(active=True)

    wb = openpyxl.Workbook()
    sheet = wb.active

    headers = [
        'Order ID',
        'Client',
        'Client Phone',
        'Created',
        'Created by',
        'Approved date',
        'Approved by',
        'Status',
        'Channel',
        'Billing address',
        'Shipping address',
        'Shipping method',
        'Shipping cost',
        'Shipping status',
        'Shipped code',
        'Total cost',
        'Total cost after discount',
        'Order discount',
        'Payable',
        'Is paid',
        'Customer notes',
        'Quantity',
        'Weight',
        'Is gift',
    ]

    for i in range(len(headers)):
        c = sheet.cell(row = 1, column = i + 1 )
        c.value = headers[i]


    for count , order in enumerate(orders):
        order.save()
        title_list = [
            order.id,
            str(order.client),
            str(order.client_phone),
            str(order.created,),
            str(order.user),
            str(order.approved_date),
            str(order.approver),
            order.status,
            order.channel,
            order.billing_address.get_full_address() if order.billing_address else '',
            order.shipping_address.get_full_address() if order.shipping_address else '',
            order.shipping_method,
            order.shipping_cost,
            order.shipping_status,
            order.shipping_code if order.shipped_code else '',
            order.total_cost,
            order.total_cost_after_discount,
            order.discount,
            order.payable,
            order.paid,
            order.customer_note,
            order.quantity,
            order.weight,
            order.is_gift,
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
    orders = Order.objects.filter(status='draft').filter(active=True)

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


def email_to_managers(paymaent_id):
    """
    Function to send email to admin when a payment is done.
    """
    payment = Payment.objects.get(pk=paymaent_id)
    order_number = '-'
    if payment.order:
        order_number = payment.order.pk

    #email body
    subject = '[Damavand] Successful payment: {} order:{}'.format(payment.id, order_number)
    # message = 'A successful payment registered at Zarinpal: \nPayment ID.: {} \nName: {} \nPhone: {} \nAmount: {:,} \n Date & Time:{} \n Ref ID.:{}'.format(
    #     payment.id,
    #     payment.client_name,
    #     payment.client_phone,
    #     payment.amount,
    #     payment.created,
    #     payment.ref_id)
    message = f"Successful payment at Zarinpal: \nPayment ID.: {payment.id} \nOrder ID.: {order_number} \nAmount: {payment.amount:,} \n\nName: {payment.client_name} \nPhone: {payment.client_phone} \n\nDate & Time:{payment.created.isoformat(sep='-')} \n Ref ID.:{payment.ref_id}"

    # send email
    # mail_managers(
    #     subject,
    #     message,
    #     fail_silently=False
    #     )
    connection = get_connection()
    connection.open()
    admin_email = EmailMessage(
        subject,
        message,
        'noreply@ketabedamavand.com',
        [
        'rahim.aghareb@gmail.com',
        'bahman.shafaa@gmail.com'
        ]
    )
    admin_email.send()
    connection.close()


def notif_email_to_managers(subject, message, recivers):
    """
    Function to send notification email to admin when it's needed.
    """

    #email body
    # subject = string
    # message = string
    # recivers = list()

    connection = get_connection()
    connection.open()
    admin_email = EmailMessage(
        subject,
        message,
        'noreply@ketabedamavand.com',
        recivers
    )
    admin_email.send()
    connection.close()


def product_export_excel(request, filter='all'):

    if filter == 'used-noprice':
        products = Product.objects.filter(available=True).filter(stock_used__gte=1).filter(price_used=0).order_by('name')
    elif filter == 'used-all':
        products = Product.objects.filter(available=True).filter(stock_used__gte=1).order_by('name')
    else:
        products = Product.objects.filter(available=True).order_by('name')

    wb = openpyxl.Workbook()
    sheet = wb.active
    if filter in ('used-noprice', 'used-all'):
        headers = [
            '#',
            'Product ID.',
            'Name',
            'isbn',
            'Publisher',
            'Main price',
            'Main stock',
            'Price used',
            'Stock used',
            'Not in market',
            'Page number',
            'Weight',
        ]
    else:
        headers = [
            '#',
            'Product ID.',
            'Name',
            'isbn',
            'Publisher',
            'Stock',
            'Price',
            'Weight',
            'size',
            'Cover type',
            'Page number',
            'Edition',
            'Other prices',
            'Price 1',
            'Stock 1',
            'Price 2',
            'Stock 2',
            'Price 3',
            'Stock 3',
            'Price 4',
            'Stock 4',
            'Price 5',
            'Stock 5',
            'Price used',
            'Stock used',
            'Not in market',
            'Available online',
            'Available in store',
            'Category',
            'Author',
            'Translator',
            'Publisher 2',
            'Publish year',
            'Product Latin name',
            'Author latin name',
            'Age range',
            'Is collection',
            'Admin note',
            'Description',
            'Import session',
        ]

    # writing header
    for i in range(len(headers)):
        c = sheet.cell(row = 1, column = i + 1 )
        c.value = headers[i]
        # c.style.fill.fill_type = Fill
        # c.style.fill.start_color.index = Color.BLUE


    # writing body
    for count , product in enumerate(products):
        # product.save()
        if filter in ('used-noprice', 'used-all'):
            title_list = [
                count,
                product.id,
                product.name,
                product.isbn,
                product.publisher,
                product.price,
                product.stock,
                product.price_used,
                product.stock_used,
                True if product.about=='*' else False,
                product.page_number,
                product.weight,
            ]
        else:
            title_list = [
                count,
                product.id,
                product.name,
                product.isbn,
                product.publisher,
                product.stock,
                product.price,
                product.weight,
                product.size,
                product.cover_type,
                product.page_number,
                product.edition,
                product.has_other_prices,
                product.price_1,
                product.stock_1,
                product.price_2,
                product.stock_2,
                product.price_3,
                product.stock_3,
                product.price_4,
                product.stock_4,
                product.price_5,
                product.stock_5,
                product.price_used,
                product.stock_used,
                True if product.about=='*' else False,
                product.available_online,
                product.available_in_store,
                str(product.category),
                product.author,
                product.translator,
                product.publisher_2,
                product.publish_year,
                product.latin_name,
                product.author_latin_name,
                product.age_range,
                product.is_collection,
                product.admin_note,
                product.description,
                str(product.import_session),
            ]
        for i in range(len(headers)):
            c = sheet.cell(row = count + 2 , column = i + 1)
            c.value = title_list[i]

    if filter=='used-noprice':
        filename = 'media/excel/used-noprice-products-{}.xlsx'.format(datetime.datetime.now().isoformat(sep='-'))
    elif filter == 'used-all':
        filename = 'media/excel/used-all-products-{}.xlsx'.format(datetime.datetime.now().isoformat(sep='-'))
    else:
        filename = 'media/excel/available-products-{}.xlsx'.format(datetime.datetime.now().isoformat(sep='-'))
    wb.save(filename)
    excel = open(filename, 'rb')
    response = FileResponse(excel)


    return response

def used_product_before_5(request):
    point = datetime.datetime.strptime('2022 3 5 16 11 26', "%Y %m %d %H %M %S")
    products = OrderLine.objects.filter(active=True).filter(created__lte=point).filter(variation__contains='used')
    print(len(products))
    # wb = openpyxl.Workbook()
    # sheet = wb.active
    #
    # headers = [
    #     '#',
    #     'Product ID.',
    #     'Name',
    #     'isbn',
    #     'Publisher',
    #     'Main price',
    #     'Main stock',
    #     'Price used',
    #     'Stock used',
    # ]
    # # writing header
    # for i in range(len(headers)):
    #     c = sheet.cell(row = 1, column = i + 1 )
    #     c.value = headers[i]
    #     # c.style.fill.fill_type = Fill
    #     # c.style.fill.start_color.index = Color.BLUE
    #
    # # making body
    # for count , product in enumerate(products):
    #     title_list = [
    #         count,
    #         product.id,
    #         str(product.product.name),
    #         product.product.isbn,
    #         product.product.publisher,
    #         product.product.price,
    #         product.product.stock,
    #         product.product.price_used,
    #         product.product.stock_used,
    #     ]
    # # writing body
    # for i in range(len(headers)):
    #     c = sheet.cell(row = count + 2 , column = i + 1)
    #     c.value = title_list[i]
    #
    # filename = 'media/excel/used-before-5-{}.xlsx'.format(datetime.datetime.now().isoformat(sep='-'))
    # wb.save(filename)
    # excel = open(filename, 'rb')
    # response = FileResponse(excel)
    #
    # return redirect('staff:products')
    return render (
        request,
        'staff/_used_before_5.html',
        {
            'products': products,
        }
    )

def qrcode_create(request, order_id, payment_id):
    order = get_object_or_404(Order, pk=order_id)
    payment = get_object_or_404(Payment, pk=payment_id)
    context = {}
    factory = qrcode.image.svg.SvgImage
    img = qrcode.make(payment.url, image_factory=factory, box_size=20)
    stream = BytesIO()
    # img.save(stream, img.format)
    img.save(stream)

    # image.save(strem)
    # context['svg'] = stream.getvalue().decode()
    # return render('staff:order_checkout', order.id)
    f = open('media/test.svg', 'w')
    f.write(stream.getvalue().decode())
    f.close()
    order.qrcode = f
    order.save()

    return render(
        request,
        'tools/qrcode_test.html',
        {
            'svg': stream.getvalue().decode()
            # 'svg': img
        }
    )
