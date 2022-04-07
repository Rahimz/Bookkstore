from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import Ticket
from .forms import CreateTicketForm

@staff_member_required
def tickets_list(request, filter=None):
    tickets = Ticket.objects.all().order_by('priority', 'rank' )
    if filter in ('normal', 'medium', 'high'):
        tickets = tickets.filter(priority=filter)


    return render(
        request,
        'tickets/tickets_list.html',
        {
            'tickets': tickets,
        }
    )


@staff_member_required
def ticket_details(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if request.method == 'POST':
        ticket_form = CreateTicketForm(
            instance=ticket,
            data=request.POST,
            files=request.FILES
        )
        if ticket_form.is_valid():
            ticket_form.save()
            # new_ticket.registrar = request.user
            # new_ticket.save()
            messages.success(request, _('Ticket updated'))
            return redirect('tickets:tickets_list')
    else:
        ticket_form = CreateTicketForm(instance=ticket)
    return render(
        request,
        'tickets/ticket_details.html',
        {
            'ticket': ticket,
            'ticket_form': ticket_form,
        }
    )


@staff_member_required
def create_ticket(request):
    if request.method == 'POST':
        ticket_form = CreateTicketForm(
            data=request.POST,
            files=request.FILES
        )
        if ticket_form.is_valid():
            new_ticket = ticket_form.save(commit=False)
            new_ticket.registrar = request.user
            new_ticket.save()
            messages.success(request, _('Ticket created'))
            return redirect('tickets:tickets_list')
    else:
        ticket_form = CreateTicketForm()
    return render (
        request,
        'tickets/create_ticket.html',
        {
            'ticket_form': ticket_form,
        }
    )
