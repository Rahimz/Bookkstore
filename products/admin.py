from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price',
                    'available', 'stock']
    list_filter = ['available', ]
    list_editable = ['price', 'available', 'stock', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    search_fields = ['name', 'author']
