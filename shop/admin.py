from django.contrib import admin

from .models import Slogan, Note

@admin.register(Slogan)
class SloganAdmin(admin.ModelAdmin):
    list_display = [
        'slogan', 'author', 'active',
    ]
    # list_filter = ['username', 'created', 'updated']
    # search_fields = ['first_name', 'last_name', 'email', 'username']
    list_editable = ['active',]

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'active'
    ]
    eidtable_fields = ['active']
