from django.contrib import admin
from .models import Category, Product, Good
import simple_history

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
class ProductAdmin(simple_history.admin.SimpleHistoryAdmin):
    list_display = ['pk', 'name', 'isbn', 'price',
                    'available', 'stock', 'updated']
    list_filter = ['available', 'stock' ]
    list_editable = ['price', 'available', 'stock',]
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name', 'created', 'updated']
    search_fields = ['name', 'author', 'isbn', 'pk', 'publisher']

@admin.register(Good)
class GoodAdmin(admin.ModelAdmin):
    list_display = ['product', 'price', 'stock']
