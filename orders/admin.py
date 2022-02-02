from django.contrib import admin
from .models import Order, OrderLine


class OrderLineInline(admin.TabularInline):
    model = OrderLine
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
