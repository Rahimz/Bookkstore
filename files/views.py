from django.shortcuts import render
from .models import File

def add_to_database(request, file=None):
    files = File.objects.all()
    return render(request,
                  'files/upload_database.html',
                  {'files': files})
