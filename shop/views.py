from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from products.models import Product, Good, Category
from search.forms import SearchForm
from cart.forms import CartAddProductForm


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

def product_list(request, category_slug=None, ):
    search_form = SearchForm()
    category = None

    if category_slug == 'new' or category_slug == 'used':
        products_object = Product.objects.filter(state=category_slug)
        page_title = category_slug
    else:
        category = get_object_or_404(Category, slug=category_slug)
        products_object = Product.objects.filter(category=category)
        page_title = category.name


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
        'shop/product_list.html',
        {
        'products':products,
        'page': page,
        'search_form': search_form,
        'category': category,
        'page_title': page_title,
        }
    )

def product_detail(request, pk, slug=None):
    product = get_object_or_404(Product, pk=pk)
    slug = product.slug
    goods = Good.objects.filter(product=product)
    cart_product_form = CartAddProductForm()
    return render(
        request,
        'shop/product_detail.html',
        {
        'product':product,
        'goods': goods,
        'cart_product_form': cart_product_form,
        }
    )

def temp_home(request):
    return render(
        request,
        'temp_home.html',
        {}
    )

def category_list(request):
    main_categories = Category.objects.filter(active=True, parent_category=None)
    
    return render(
        request,
        'shop/category_list.html',
        {'main_categories': main_categories }
    )
