from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from products.models import Product, Good
from search.forms import SearchForm


def home(request):
    search_form = SearchForm()

    products_object = Product.objects.all()
    # pagination
    paginator = Paginator(products_object, 20) # 20 posts in each page
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        products = paginator.page(paginator.num_pages)
    return render(
        request,
        'home.html',
        {
        'products':products,
        'page': page,
        'search_form': search_form,
        }
    )


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    goods = Good.objects.filter(product=product)
    return render(
        request,
        'shop/product_detail.html',
        {
        'product':product,
        'goods': goods,
        }
    )

def temp_home(request):
    return render(
        request,
        'temp_home.html',
        {}
    )
