from django.contrib import admin

from .models import CustomUser, Address


# admin.site.register(CustomUser)

admin.site.register(Address)

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
