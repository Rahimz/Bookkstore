from django.contrib import admin
from .models import Category, Product, Good, Craft
import simple_history

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
class ProductAdmin(simple_history.admin.SimpleHistoryAdmin):
    list_display = ['pk', 'name', 'isbn', 'price', 'stock',
                    'available', 'price_used', 'stock_used', 'has_other_prices', 'updated']
    list_filter = ['available', 'stock' ]
    list_editable = ['price', 'available', 'stock', 'price_used', 'stock_used', 'has_other_prices',]
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name', 'created', 'updated']
    search_fields = ['name', 'author', 'isbn', 'pk', 'publisher']

@admin.register(Good)
class GoodAdmin(admin.ModelAdmin):
    list_display = ['product', 'price', 'stock']


@admin.register(Craft)
class CraftAdmin(admin.ModelAdmin):
    list_display = ['name',  'available', 'category']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['available', 'category']
    search_fields = ['name', 'pk', 'category',]
