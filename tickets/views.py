from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import Ticket
from .forms import CreateTicketForm

@staff_member_required
def tickets_list(request):
    tickets = Ticket.objects.all().order_by('rank')

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
    return render(
        request,
        'tickets/ticket_details.html',
        {
            'ticket': ticket,
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
            ticket_form.save()
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
