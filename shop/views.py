from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from products.models import Product, Good, Category, Image
from search.forms import SearchForm
from cart.forms import CartAddProductForm
from search.views import ProductSearch
from .models import Note

def home(request):
    search_form = SearchForm()

    products_object = Product.objects.all().filter(available=True)
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

    if category_slug == 'used':
        products_object = Product.objects.filter(available=True).exclude(product_type='craft').filter(stock_used__gte=1)
        page_title = category_slug
    elif category_slug == 'new':
        products_object = Product.objects.filter(available=True).exclude(product_type='craft').filter(Q(stock__gte=1) | Q(stock_1__gte=1) | Q(stock_2__gte=1) | Q(stock_3__gte=1) | Q(stock_4__gte=1) | Q(stock_5__gte=1))
        page_title = category_slug

    else:
        category = Category.objects.filter(slug=category_slug).values_list('id', flat=True)
        products_object = Product.objects.all().filter(available=True).filter( Q(category__id__in=category) | Q(sub_category__id__in=category))
        page_title = category_slug


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

def product_detail(request, product_id, slug=None, image_id=None):

    product = get_object_or_404(Product, pk=product_id)
    slug = product.slug
    # goods = Good.objects.filter(product=product)
    cart_product_form = CartAddProductForm()
    product_images = product.images.all().filter(main_image=False)
    # product_images = Image.objects.filter(product=product)

    try:
        first_image = product.images.get(main_image=True)
    except:
        first_image = None
    if image_id:
        main_image = get_object_or_404(Image, pk=image_id)
        # print(main_image.id)
    else:
        try:
            main_image = product.images.get(main_image=True)
        except:
            main_image = None

    return render(
        request,
        'shop/product_detail.html',
        {
        'product':product,
        # 'goods': goods,
        'cart_product_form': cart_product_form,
        'first_image': first_image,
        'main_image': main_image,
        'product_images': product_images,
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
    search_form = SearchForm()
    return render(
        request,
        'shop/category_list.html',
        {'main_categories': main_categories,
        'search_form': search_form }
    )


def store_book_search(request, state):
    # products = Product.objects.all().filter(available=True).filter(stock_used__isnull=False)
    note = None

    try:
        note = get_object_or_404(Note, tag='clients')
    except:
        pass

    all_products = None
    new_products = None
    used_products = None
    products = None
    all_quantity = 0
    if request.method == 'POST':
        search_form = SearchForm(data=request.POST)
        if search_form.is_valid():
            search_query = search_form.cleaned_data['query']
            if search_query == ' ':
                return redirect('shop:store_book_search', 'used')

            # all_products = ProductSearch(object=Product, query=search_query).order_by('name', 'publisher')
            new_products = ProductSearch(object=Product, query=search_query).filter(
                Q(stock__gte=1) | Q(stock_1__gte=1) | Q(stock_2__gte=1) | Q(stock_3__gte=1) | Q(stock_4__gte=1) | Q(stock_5__gte=1)).exclude(product_type='craft').order_by('name', 'publisher')
            used_products = ProductSearch(object=Product, query=search_query).filter(stock_used__gte=1).exclude(product_type='craft').order_by('name', 'publisher')
            all_quantity = new_products.count() + used_products.count()
            search_form = SearchForm()

    else:
        search_form = SearchForm()

    return render(
        request,
        'shop/store_book_search.html',
        {
            'products': products,
            # 'all_products': all_products,
            'state': state,
            'search_form': search_form,
            'note': note,
            'new_products': new_products,
            'used_products': used_products,
            'all_quantity': all_quantity,
        }
    )
