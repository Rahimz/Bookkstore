from django.shortcuts import render


def home(request):
    return render(
        request,
        'home.html',
        {}
    )


def product_detail(request):
    return render(
        request,
        'shop/product_detail.html',
        {}
    )
