from django.shortcuts import render

from .models import Ticket

def tickets_list(request):
    tickets = Ticket.objects.all().order_by('rank')

    return render(
        request,
        'tickets/tickets_list.html',
        {
            'tickets': tickets,
        }
    )
