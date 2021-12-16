from django.shortcuts import render, get_object_or_404
from products.models import Product


def home(request):
    products = Product.objects.all()
    return render(
        request,
        'home.html',
        {
        'products':products,
        }
    )


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(
        request,
        'shop/product_detail.html',
        {
        'product':product,
        }
    )

def temp_home(request):
    return render(
        request,
        'temp_home.html',
        {}
    )
