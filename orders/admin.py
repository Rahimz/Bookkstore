from django.contrib import admin
from .models import Order, OrderLine, Purchase, PurchaseLine


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    raw_id_fields = ['product']


class PurchaseLineInline(admin.TabularInline):
    model = PurchaseLine
    raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'client', 'user',
        'user_email', 'paid', 'approved_date',
    ]
    list_filter = ['paid', 'approved_date', ]
    list_editable = ['paid', 'approved_date', ]
    search_fields = ['first_name', 'last_name', 'email']
    inlines = [OrderLineInline]


@admin.register(OrderLine)
class OrderLineAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'order', 'product',
        'price', 'quantity', 'variation',
    ]
    search_fields = ['order', 'product', 'variation']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = [
        'pk', 'vendor'
    ]
    inlines = [PurchaseLineInline]


@admin.register(PurchaseLine)
class PurchaseLineAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'purchase', 'product',
        'price', 'quantity', 'variation',
    ]
    search_fields = ['purchase', 'product', 'variation']
