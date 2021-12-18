from django.contrib import admin
from .models import File, ImportSession

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['name', 'type']

@admin.register(ImportSession)
class ImportSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'created', 'quantity']
    search_fileds =['user', 'created']
