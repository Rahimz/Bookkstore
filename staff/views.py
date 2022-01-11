from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.postgres.search import SearchVector
from django.db.models import Q
import uuid

from .forms import ProductCreateForm, OrderCreateForm
from products.models import Product, Category
from orders.models import Order, OrderLine
from orders.forms import OrderAdminCheckoutForm
from search.forms import ClientSearchForm, BookIsbnSearchForm
from account.models import CustomUser


def sales(request):
    return render(
        request,
        'staff/sales.html',
        {}
    )


def orders(request):
    orders = Order.objects.filter(
        Q(status='approved') | Q(paid=True))
    return render(
        request,
        'staff/orders.html',
        {'orders': orders}
    )

def order_detail_for_admin(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(
        request,
        'staff/order_detail_for_admin.html',
        {'order': order}
    )

def purchases(request):
    return render(
        request,
        'staff/purchases.html',
        {}
    )

def warehouse(request):
    return render(
        request,
        'staff/warehouse.html',
        {}
    )

def products(request):
    products_object = Product.objects.all()
    # pagination
    paginator = Paginator(products_object, 50) # 50 posts in each page
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
        'staff/products.html',
        {
        'products':products,
        'page': page,
        }
    )


def product_create(request):
    if request.method == 'POST':
        form = ProductCreateForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.category = Category.objects.get(name=form.cleaned_data['category'])

            product.save()
            messages.success(request, 'Product is created!')
            return HttpResponseRedirect(reverse('staff:products'))
        else:
            messages.error(request, 'Form is not valid')
    else:
        form = ProductCreateForm()
    return render(
        request,
        'staff/product_create.html',
        {'form': form }
    )


def order_create(request):
    form = OrderCreateForm()
    return render(
        request,
        'staff/order_create.html',
        {'form': form}
    )

class ProductCreate(View):
    # template = 'staff/product_create.html'

    def get(self, request):
        return reverse('staff:product_create')
    def post(self, request):
        if request.method == 'POST':
            form = ProductCreateForm()
            if form.is_valid:
                product = form.save(commit=False)
                product.save()
                messages.success(request, 'Product is created!')
        if "cancel" in request.POST:
            return HttpResponseRedirect(reverse('staff:products'))
        return super(ProductCreate, self).post(request, *args, **kwargs)


    def get_success_url(self):
        if "another" in self.request.POST:
            return reverse('staff:product_create')
        # else return the default `success_url`
        return super(ProductCreate, self).get_success_url()


        if request.method == 'POST':
            form = ProductCreateForm()
            if form.is_valid():
                product = form.save()
                messages.success(request, 'Product created')
                return HttpResponseRedirect(reverse('shop:home'))
            else:
                messages.error(request, 'Product dose not created!')
        else:
            form = ProductCreateForm()
        return render(
            request,
            'staff/product_create.html',
            {'form': form}
        )

def invoice_create(request, order_id=None):
    if order_id:
        order = Order.objects.get(pk=order_id)
    else:
        order = None

    isbn_search_form = BookIsbnSearchForm()

    books = None
    book = None
    isbn = ''
    if request.method == 'POST':
        isbn_search_form =BookIsbnSearchForm(data=request.POST)
        client_form = ClientSearchForm(data=request.POST)

        if isbn_search_form.is_valid():
            isbn = isbn_search_form.cleaned_data['isbn_query']
            if not order:
                order = Order.objects.create(
                            user = request.user,
                            status = 'draft',
                            shipping_method = 'pickup',
                        )
                messages.success(request, 'order No. {} is created'.format(order.id))

            try:
                book = Product.objects.get(isbn=isbn)
                messages.success(request, 'Book {} found'.format(book.id))
                order_line = OrderLine.objects.create(
                    order = order,
                    product = book,
                    quantity = 1,
                    price = book.price,
                )
                messages.success(request,'order line No. {} with {} is added'.format(order.id, book))

                isbn_search_form = BookIsbnSearchForm()

            except:
                messages.error(request, 'Book {} does not exist!'.format(isbn))

    return render(
        request,
        'staff/invoice_create.html',
        {'order': order,
         'isbn_search_form': isbn_search_form,
         'isbn': isbn,
    })


def invoice_checkout(request, order_id):
    checkout_form = OrderAdminCheckoutForm()
    client_search_form = ClientSearchForm()
    client = CustomUser.objects.get(username='guest')
    order = Order.objects.get(pk=order_id)
    if request.method == 'POST':
        checkout_form = OrderAdminCheckoutForm(data=request.POST)
        client_search_form = ClientSearchForm(data=request.POST)
        if client_search_form.is_valid():
            messages.debug(request, 'client_search_form.is_valid')
            query = client_search_form.cleaned_data['query']
            try:
                client = CustomUser.objects.get(
                    Q(phone=query) | Q(first_name=query) | Q(last_name=query) | Q(username=query)
                    )
                messages.success(request, 'client found')
            except:
                pass
        if checkout_form.is_valid():
            messages.debug(request, 'checkout_form.is_valid')
            order.client = client
            order.paid = checkout_form.cleaned_data['paid']
            order.customer_note = checkout_form.cleaned_data['customer_note']
            order.status = 'approved'
            shipping_method = 'pickup'
            order.save()
            messages.success(request, 'Order approved')
            return redirect('staff:order_list')
    return render(
        request,
        'staff/invoice_checkout.html',
        {'client_search_form': client_search_form,
         'order': order,
         'checkout_form': checkout_form,
    })


def draft_orders(request):
    draft_orders = Order.objects.filter(status='draft')
    return render(
        request,
        'staff/draft_orders.html',
        {'draft_orders': draft_orders}
    )
