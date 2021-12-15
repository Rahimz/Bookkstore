from django.shortcuts import render, get_object_or_404
from django.conf import settings
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from openpyxl import load_workbook
from io import BytesIO

from .models import File as FileObject
from django.core.files import File

def add_to_database(request, file_slug=None):
    """
    This Function is designed to import datat from excel.
    The imported datat is very different, so we grab every files
    and check the headers and import file in a manual method.
    """
    files = FileObject.objects.all()
    file_object = None
    row = None
    if file_slug:
        file_object = get_object_or_404(FileObject, slug=file_slug)
        # f = file_object.path
        myfile = File(file_object)
        # myfile.open('rb').readlines()
        path = file_object.file.path
        with open(path, 'rb') as f:
            wb = load_workbook(f)
            ws = wb.active
            row = ws['A2'].value
        # myfile.close()
    return render(request,
                  'files/upload_database.html',
                  {'files': files,
                   'file_object': file_object,
                   'row': row
                   })
