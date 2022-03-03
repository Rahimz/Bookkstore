from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib import messages
import uuid
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.postgres.search import SearchVector

from .forms import LoginForm, UserRegistrationForm, UserEditForm, ClientAddForm, ClientUpdateForm, AddressAddForm
from .models import CustomUser, Address
from search.forms import CLientSearchStaffForm
from tools.fa_to_en_num import number_converter


def dashboard(request):
    user = request.user
    return render(request,
                  'account/dashboard.html',
                  {})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(user_form.cleaned_data['password'])

            new_user.is_client = True
            # Save the User object
            new_user.save()

            # TODO: The registraion email does not recieve in mailbox
            if new_user.email:
                subject = "You are registered at Ketabedamavand.com"
                to = new_user.email
                html_content = render_to_string(
                    'tools/emails/registration_email.html', {'user': new_user})
                # Strip the html tag. So people can see the pure text at least.
                text_content = strip_tags(html_content)

                msg = EmailMultiAlternatives(subject, text_content, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()

            return render(request,
                          'account/register_done.html',
                          {'new_user': new_user})
        else:
            messages.error(request, _('Form is not valid'))
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'account/register.html',
                  {'user_form': user_form})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)

        if user_form.is_valid():
            user_form.save()

            # https://docs.djangoproject.com/en/2.0/ref/contrib/messages/
            messages.success(request, _('User details updated successfully'))
        else:
            messages.error(request, _('Error updating your user details'))
    else:
        user_form = UserEditForm(instance=request.user)

    return render(request,
                  'account/edit.html',
                  {'user_form': user_form,
                   })

# def password_reset(request):
#     form = PasswordResetForm()
#     if request.method == "POST":
#         form = PasswordResetForm(data=request.POST)
#         if form.is_valid():
#             send_mail(to_email=form.email)
#     return render(
#         request,
#         'registration/password_reset_form.html',
#         {'form': form}
#     )


@staff_member_required
def client_list(request):
    results = None
    clients = CustomUser.objects.filter(is_client=True).order_by('-pk').exclude(is_superuser=True).exclude(username='guest')

    if request.method == 'POST':
        client_search_form = CLientSearchStaffForm(data=request.POST)
        if client_search_form.is_valid():
            query = client_search_form.cleaned_data['query']

            # we will check if any farsi character is in the query we will changed it
            query = number_converter(query)

            clients = clients.annotate(
                search=SearchVector('first_name', 'last_name', 'username', 'phone', 'social_media_name'),).filter(search__contains=query)
    else:
        client_search_form = CLientSearchStaffForm()

    return render(
        request,
        'account/clients/client_list.html',
        {'clients': clients,
         'client_search_form': client_search_form,
         'results': results
         }
    )


def client_add(request):
    form = ClientAddForm()
    # billing_address_form = AddressAddForm()
    # shipping_address_form = AddressAddForm()

    if request.method == "POST":
        client_form = ClientAddForm(data=request.POST)
        # billing_address_form = AddressAddForm(data=request.POST)
        # shipping_address_form = AddressAddForm(data=request.POST)

        if client_form.is_valid():
            new_client = client_form.save(commit=False)
            new_client.is_client = True
            new_client.username = client_form.cleaned_data['phone']
            new_client.phone = client_form.cleaned_data['phone']
            new_client.first_name = client_form.cleaned_data['first_name']
            new_client.last_name = client_form.cleaned_data['last_name']
            new_client.password = str(uuid.uuid4())
            new_client.email = "{}@ketabedamavand.com".format(
                new_client.username)

            new_client.save()


            messages.success(request, _('Client added!'))
            return redirect('/account/clients/#clientTable')
        else:
            client_form = ClientAddForm(data=request.POST)
            messages.error(request, _('The phone number is already used!'))
    else:
        client_form = ClientAddForm()
    return render(
        request,
        'account/clients/client_add.html',
        {'client_form': client_form,
         # 'billing_address_form': billing_address_form,
         # 'shipping_address_form': shipping_address_form,
         }
    )


def client_update(request, client_id):
    client = CustomUser.objects.get(pk=client_id)

    if request.method == "POST":
        client_form = ClientUpdateForm(data=request.POST, instance=client)

        if client_form.is_valid():
            client_form.save()

            messages.success(request, _('Client details updated'))
            return redirect('/account/clients')
        else:
            messages.error(request, _('Form is not valid'))
    else:
        client_form = ClientUpdateForm(instance=client)

    return render(
        request,
        'account/clients/client_add.html',
        {'client': client,
         'client_form': client_form,

         }
    )


def client_details(request, client_id):
    client = CustomUser.objects.get(pk=client_id)
    return render(
        request,
        'account/clients/client_details.html',
        {
            'client': client,
        }
    )

def client_add_address(request, client_id, kind, address_id=None):
    client = CustomUser.objects.get(pk=client_id)
    if address_id:
        address = Address.objects.get(pk=address_id)
    # address_form = AddressAddForm()
    if request.method == 'POST':
        if address_id:
            address_form = AddressAddForm(data=request.POST, instance=address)
        else:
            address_form = AddressAddForm(data=request.POST, initial={'kind': kind})

        if address_form.is_valid():
            new_address = address_form.save(commit=False)
            if not new_address.address_phone:
                new_address.phone = client.phone
            new_address.save()

            if kind == 'billing':
                client.default_billing_address = new_address
            elif kind == 'shipping':
                client.default_shipping_address = new_address
            client.addresses.add(new_address)
            client.save()
            messages.success(request, _('Address added to client details'))
            return redirect('client_details', client.id)
    else:
        if address_id:
            address_form = AddressAddForm(instance=address)
        else:
            address_form = AddressAddForm(initial={'kind':kind})
    return render(
        request,
        'account/clients/client_add_address.html',
        {
            'address_form': address_form,
            'kind': kind,
            'client': client,
        }
    )
