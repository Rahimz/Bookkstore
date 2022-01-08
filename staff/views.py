from django.shortcuts import render, reverse, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.postgres.search import SearchVector
from django.db.models import Q

from .forms import ProductCreateForm, OrderCreateForm
from products.models import Product, Category
from orders.models import Order
from search.forms import ClientSearchForm
from account.models import CustomUser


def sales(request):
    return render(
        request,
        'staff/sales.html',
        {}
    )


def orders(request):
    orders = Order.objects.filter(paid=True)
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
                message.success(request, 'Product is created!')
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

def invoice_create(request):
    client_search_form = ClientSearchForm()
    client = None
    if request.method == 'POST':
        client_form = ClientSearchForm(data=request.POST)
        if client_form.is_valid():
            query = client_form.cleaned_data['query']
            # client = CustomUser.objects.all().annotate(
            #     search=SearchVector('phone')).get(search=query)
            try:
                client = CustomUser.objects.get(
                    Q(phone=query) | Q(first_name=query) | Q(last_name=query) | Q(username=query)
                )
            except:
                message.error(request, 'Client does not exist!')

    return render(
        request,
        'staff/invoice_create.html',
        {'client_search_form': client_search_form,
         'client': client,
    })
