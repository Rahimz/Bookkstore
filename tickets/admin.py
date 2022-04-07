from django.contrib import admin
from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'registrar',
        'is_checked', 'is_solved', 'active'
    ]
    list_filter = [
        'is_checked', 'is_solved', 'active'
    ]
    search_fields = [
        'name', 'description'
    ]
