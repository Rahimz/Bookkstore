from django.shortcuts import render
from django.contrib.postgres.search import SearchVector

from products.models import Product
from .forms import SearchForm


def product_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Product.objects.all().annotate(
                search=SearchVector('name', 'author', 'translator', 'publisher', ),
            ).filter(search=query)
    return render(request,
                  'search/search.html',
                  {'form': form,
                   'query': query,
                   'results': results,
                   })