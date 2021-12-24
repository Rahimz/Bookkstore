from django.shortcuts import render

# Create your views here.


def sales(request):
    return render(
        request,
        'staff/staff_orders.html',
        {}
    )
