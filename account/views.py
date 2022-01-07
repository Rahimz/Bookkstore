from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail
from django.contrib import messages
import uuid
from django.urls import reverse

from .forms import LoginForm, UserRegistrationForm, UserEditForm, ClientAddForm
from .models import CustomUser


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
            # Save the User object
            new_user.save()

            return render(request,
                         'account/register_done.html',
                         {'new_user': new_user})
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
            messages.success(request,
                            'User details updated successfully')
        else:
            messages.error(request, 'Error updating your user details')
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

def client_list(request):
    clients = CustomUser.objects.filter(is_client=True)
    return render(
        request,
        'account/clients/client_list.html',
        {'clients': clients}
    )

def client_add(request):
    form = ClientAddForm()
    if request.method == "POST":
        form = ClientAddForm(data=request.POST)
        try:
            if form.is_valid():
                new_client = form.save(commit=False)
                new_client.is_client = True
                new_client.username = form.cleaned_data['phone']
                new_client.password = str(uuid.uuid4())
                new_client.email = "{}@ketabedamavand.com".format(new_client.username)
                new_client.save()
                messages.success(request, 'Client added!')
                return redirect('/account/clients')
        except:
            form = form = ClientAddForm(data=request.POST)
            messages.error(request, 'the phone number is already used!')
    else:
        form = ClientAddForm()
    return render(
        request,
        'account/clients/client_add.html',
        {'form': form}
    )
