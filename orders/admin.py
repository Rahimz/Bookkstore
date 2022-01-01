from django.contrib import admin
from .models import Order, OrderLine


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'client', 'user',
        'user_email', 'paid', 'created', 'updated'
    ]
    list_filter = ['paid', 'created', 'updated']
    search_fields = ['first_name', 'last_name', 'email']
    inlines = [OrderLineInline]
