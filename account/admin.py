from django.contrib import admin

from .models import CustomUser, Address, Vendor, Credit


# admin.site.register(CustomUser)

# admin.site.register(Address)

@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'username', 'is_staff', 'is_client', 'first_name', 'last_name',
        'email',
    ]
    # list_filter = ['username', 'created', 'updated']
    search_fields = ['first_name', 'last_name', 'email', 'username']
    list_editable = ['is_staff', 'is_client',]
    # inlines = [OrderLineInline]


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'overal_discount']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name']

@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'orders_sum', 'order_count']
