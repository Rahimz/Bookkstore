from django.contrib import admin

from .models import Warehouse, Refund


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = [
        'name'
    ]
    # search_fields = ['order', 'product', 'variation']


@admin.register(Refund)
# class ProductAdmin(admin.ModelAdmin):
class RefundAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'order', 'purchase',
        'quantity', 'price', 'from_client',
         'to_vendor']
    # list_filter = ['available', 'stock' ]
    # list_editable = ['price', 'available', 'stock',]
    # prepopulated_fields = {'slug': ('name',)}
    # ordering = ['name', 'created', 'updated']
    # search_fields = ['name', 'author', 'isbn']
