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
        'paid', 'active',
    ]
    list_filter = ['paid', 'active', 'status', 'approved_date',  ]
    # list_editable = ['paid', ]
    search_fields = ['client', 'pk', 'user']
    inlines = [OrderLineInline]

    class Meta:
        ordering = ['created']


@admin.register(OrderLine)
class OrderLineAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'order', 'product', 'active',
        'price', 'quantity', 'variation',
    ]
    search_fields = ['order', 'product', 'variation']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = [
        'pk', 'vendor', 'paper_invoice_number'
    ]
    inlines = [PurchaseLineInline]


@admin.register(PurchaseLine)
class PurchaseLineAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'purchase', 'product',
        'price', 'quantity', 'discount', 'discount_percent', 'variation',
    ]
    search_fields = ['purchase', 'product', 'variation']
