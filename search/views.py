from django.shortcuts import render
from django.contrib.postgres.search import SearchVector

from products.models import Product
from .forms import SearchForm


def ProductSearch(object, query):
    """
    Search an object model base on a search query
    """
    results = object.objects.all().filter(available=True).annotate(
        search=SearchVector('name', 'author', 'translator', 'publisher', 'isbn', 'isbn_9'),
    ).filter(search=query)
    return results

def product_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = ProductSearch(object=Product, query=query)
            # results = Product.objects.all().annotate(
            #     search=SearchVector('name', 'author', 'translator', 'publisher', 'isbn'),
            # ).filter(search=query)
    return render(request,
                  'search/search.html',
                  {'form': form,
                   'query': query,
                   'results': results,
                   })
