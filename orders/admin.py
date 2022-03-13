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
    search_fields = ['client__first_name', 'client__last_name', 'pk', 'user__first_name', 'user__last_name']
    inlines = [OrderLineInline]

    class Meta:
        ordering = ['created']


@admin.register(OrderLine)
class OrderLineAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'order', 'product', 'active',
        'price', 'quantity', 'variation',
    ]
    search_fields = ['order__id', 'product__name', 'variation']
    list_filter = ['active', ]


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = [
        'pk', 'vendor', 'paper_invoice_number', 'created', 'quantity', 'active'
    ]
    search_fields = ['pk', 'vendor__first_name', 'paper_invoice_number']
    list_filter = ['active', 'vendor']
    inlines = [PurchaseLineInline]


@admin.register(PurchaseLine)
class PurchaseLineAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'purchase', 'product',
        'price', 'quantity', 'discount', 'discount_percent', 'variation',
    ]
    search_fields = ['purchase__id', 'product__name', 'variation']
    list_filter = ['active', ]
