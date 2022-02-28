from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, reverse
from zeep import Client
import requests
import json
import datetime
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from orders.models import Order
# from .tasks import payment_completed
from config.settings.secrets import *
from .forms import PaymentForm
from .models import Payment
from tools.views import email_to_managers


MERCHANT = merchant
ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"
if settings.DEBUG:
    CallbackURL = 'http://localhost:8000/zarinpal/verify/'
else:
    CallbackURL = 'https://ketabedamavand.com/zarinpal/verify/'
# client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')

# we use this variable to edit order after the successful payment
paid_order = None
# we get the amount from request so we dont have it when we
# back from payment port. So we keep amount and description
# in the another variable
# global_amount = [amount, order_id, order_paid]
global_amount = [0, 0, None]


payment_data = {'id': 0}

global_description = ''


def send_form_request(request, pay_id=None):
    request.session['paid'] = None
    if pay_id:
        payment_id = pay_id
    else:
        payment_id = payment_data['id']
    payment = Payment.objects.get(pk=payment_id)
    if payment.paid == True:
        # return redirect('already_paid')
        #we will retrun a function in this views.py
        return already_paid(request, payment.id)
    request.session['payment_id'] = payment.id
    description = payment.client_name
    amount = payment.amount
    mobile = payment.client_phone

    if settings.DEBUG:
        CallbackURL = 'http://localhost:8000/zarinpal/form_verify/'
    else:
        CallbackURL = 'https://ketabedamavand.com/zarinpal/form_verify/'

    # send request to payment system
    req_data = {
        "merchant_id": MERCHANT,
        "amount": amount,
        "callback_url": CallbackURL,
        "description": description,
        "metadata": {"mobile": str(mobile),}
    }
    req_header = {"accept": "application/json",
                  "content-type": "application/json'"}
    req = requests.post(url=ZP_API_REQUEST,
                        data=json.dumps(req_data),
                        headers=req_header)
    authority = req.json()['data']['authority']

    if len(req.json()['errors']) == 0:
        return redirect(ZP_API_STARTPAY.format(authority=authority))
    else:
        e_code = req.json()['errors']['code']
        e_message = req.json()['errors']['message']
        return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")

def form_verify(request):
    payment = None



    t_status = request.GET.get('code')
    t_authority = request.GET['Authority']

    if request.GET.get('Status') == 'OK':
        payment_id = request.session['payment_id']
        payment = Payment.objects.get(pk=payment_id)
        amount = payment.amount

        req_header = {"accept": "application/json",
                      "content-type": "application/json'"}
        req_data = {
            "merchant_id": MERCHANT,
            "amount": amount,
            "authority": t_authority
        }
        req = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
        if len(req.json()['errors']) == 0:
            t_status = req.json()['data']['code']
            if t_status == 100:
                # These modification should happen to paid order
                request.session['paid'] = True
                payment.ref_id = request.GET['Authority']
                payment.paid = True
                if payment.order:
                    order = payment.order
                    order.paid = True
                    order.save()
                payment.save()

                # send the result to admins
                email_to_managers(payment.id)

                return render(request, 'zarinpal/form_success.html',
                              {'message': _('Transaction success.\nRefID: ') +
                                           str(req.json()['data']['ref_id']),
                               'payment': payment})

            elif t_status == 101:

                # These modification should happen to paid order
                request.session['paid'] = True
                payment.ref_id = request.GET['Authority']
                payment.paid = True
                if payment.order:
                    order = payment.order
                    order.paid = True
                    order.save()
                payment.save()

                # send the result to admins
                email_to_admin(payment.id)

                return render(request, 'zarinpal/form_success.html',
                              {'message': _('Transaction submitted : ') +
                                          str(req.json()['data']['message']),
                               'payment': payment})

            else:
                return render(request,
                              'zarinpal/form_fail.html',
                              {'message': str (req.json()['data']['message'])})

        else:
            e_code = req.json()['errors']['code']
            e_message = req.json()['errors']['message']

            return render(request,
                          'zarinpal/form_fail.html',
                          {'message': f"Error code: {e_code}, Error Message: {e_message}",
                          'amount': req_data['amount'],
                          'authority': req_data['authority'],
                           })
    else:
        return render(request, 'zarinpal/form_fail.html',
                      {'message': _('Transaction failed or canceled by user')})


def send_request(request):
    # we get the order detail from session
    order_id = request.session.get('order_id')
    global_amount[1] = order_id
    order = get_object_or_404(Order, id=order_id)
    # 25 hezar toman for shipping added
    amount = int(order.get_total_cost()) * 10  # Toman / Required

    # put the amount to global_amount for use in verify function
    # global_amount = amount
    global_amount[0] = amount

    paid_order = order

    # set the order in the session
    request.session['order_id'] = order.id
    request.session['order_paid'] = None

    description = "سفارش شماره {}".format(order.id)  # Required
    # put the description in global_description to use n verify function
    global_description = description
    email = order.email  if order.email else ''  # Optional
    mobile = order.phone if order.phone else ''  # Optional

    # send request to payment system
    req_data = {
        "merchant_id": MERCHANT,
        "amount": amount,
        "callback_url": CallbackURL,
        "description": description,
        # "metadata": {"mobile": mobile, "email": email}
    }
    req_header = {"accept": "application/json",
                  "content-type": "application/json'"}
    req = requests.post(url=ZP_API_REQUEST,
                        data=json.dumps(req_data),
                        headers=req_header)
    authority = req.json()['data']['authority']

    if len(req.json()['errors']) == 0:
        return redirect(ZP_API_STARTPAY.format(authority=authority))
    else:
        e_code = req.json()['errors']['code']
        e_message = req.json()['errors']['message']
        return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")




def verify(request):
    amount = global_amount[0]
    order_id = global_amount[1]
    description = global_description
    t_status = request.GET.get('Status')
    t_authority = request.GET['Authority']
    if request.GET.get('Status') == 'OK':
        req_header = {"accept": "application/json",
                      "content-type": "application/json'"}
        req_data = {
            "merchant_id": MERCHANT,
            "amount": amount,
            "authority": t_authority
        }
        req = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
        if len(req.json()['errors']) == 0:
            t_status = req.json()['data']['code']
            if t_status == 100:

                # These modification should happen to paid order
                request.session['order_paid'] = True
                order = Order.objects.get(id=order_id)
                order.paid = True
                order.updated = datetime.datetime.now()
                order.save()

                return render(request, 'zarinpal/success.html',
                              {'message': _('Transaction success.\nRefID: ') +
                                           str(req.json()['data']['ref_id']),
                               'order': order})

            elif t_status == 101:

                # These modification should happen to paid order
                request.session['order_paid'] = True
                order = Order.objects.get(id=order_id)
                order.paid = True
                order.updated = datetime.datetime.now()
                order.save()

                # return render(request, 'zarinpal/success.html',
                #               {'message': 'Transaction success.\nRefID: ' +
                #                            str(req.json()['data']['ref_id']),
                #                'order': order})
                return render(request, 'zarinpal/success.html',
                              {'message': _('Transaction submitted : ') +
                                          str(req.json()['data']['message']),
                               'order': order})

            else:
                return render(request,
                              'zarinpal/fail.html',
                              {'message': str (req.json()['data']['message'])})

        else:
            e_code = req.json()['errors']['code']
            e_message = req.json()['errors']['message']

            return render(request,
                          'zarinpal/fail.html',
                          {'message': f"Error code: {e_code}, Error Message: {e_message}",
                          'amount': req_data['amount'],
                          'authority': req_data['authority'],
                           })
    else:
        return render(request, 'zarinpal/fail.html',
                      {'message': _('Transaction failed or canceled by user')})


def form_payment(request):
    form = PaymentForm()
    if request.method == 'POST':
        form = PaymentForm(data=request.POST)
        if form.is_valid():
            new_payment = form.save()
            payment_data['id'] = new_payment.id
            # return redirect(reverse('zarinpal:request'))
            return send_form_request(request)
    else:
        form = PaymentForm()

    return render(
        request,
        'zarinpal/form_payment.html',
        {'form': form}
    )


def payment_create(request):
    form = PaymentForm()
    if request.method == 'POST':
        form = PaymentForm(data=request.POST)
        if form.is_valid():
            new_payment = form.save()
            return redirect('zarinpal:payment_list')
    else:
        form = PaymentForm()

    return render(
        request,
        'zarinpal/payment_create.html',
        {'form': form}
    )


def payment_create_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    payment = None
    # if payment:
    #     messages.warning(request, _('This payment is created before with number: ') + f"{payment.pk}")
    #     return redirect('zarinpal:payment_list')
    try:
        payment = Payment.objects.get(order=order)
        if payment:
            messages.warning(request, _('This payment is created before with number: ') + f"{payment.pk}")
            return redirect('zarinpal:payment_list')
    except:
        pass


    Payment.objects.create(
        client_name=f"{order.client.first_name} {order.client.last_name}",
        client_phone=order.client.phone,
        order=order,
        amount=order.payable,
        url=request.build_absolute_uri()
        # url=request.get_absolute_url('zarinpal:payment_create_order', order.id )
    )
    messages.success(request, _('Payment link is created'))
    return redirect('zarinpal:payment_list')


def payment_list(request):
    payments = Payment.objects.all().order_by('-created')
    return render(
        request,
        'zarinpal/payment_list.html',
        {'payments': payments}
    )


def already_paid(request, payment_id):
    return render(
        request,
        'zarinpal/already_paid.html',
        {'payment_id': payment_id}
    )
