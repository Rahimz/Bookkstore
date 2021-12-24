from django.shortcuts import render

# Create your views here.


def orders(request):
    return render(
        request,
        'staff/staff_orders.html',
        {}
    )


def purchases(request):
    return render(
        request,
        'staff/purchase_orders.html',
        {}
    )

def warehouse(request):
    return render(
        request,
        'staff/warehouse.html',
        {}
    )
