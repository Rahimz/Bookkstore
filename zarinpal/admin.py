from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'pk', 'amount', 'client_name', 'paid', 'ref_id', 'order', 'url'
    ]
    # list_filter = ['paid', 'created', 'updated']
    # search_fields = ['first_name', 'last_name', 'email']
