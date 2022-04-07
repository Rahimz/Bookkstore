from django.shortcuts import render


def tickets_list(request):
    return render(
        request,
        'tickets/tickets_list.html'
    )
