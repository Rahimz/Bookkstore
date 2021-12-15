from django.shortcuts import render, get_object_or_404
from django.conf import settings
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from openpyxl import load_workbook
from io import BytesIO

from .models import File as FileObject
from django.core.files import File

from products.models import Product, Category

def add_to_database(request, file_slug=None):
    """
    This Function is designed to import datat from excel.
    The imported datat is very different, so we grab every files
    and check the headers and import file in a manual method.
    """
    files = FileObject.objects.all()
    file_object = None
    row = None
    test_object = None
    barcode_number_list =['9780000002457']
    if file_slug:
        file_object = get_object_or_404(FileObject, slug=file_slug)
        # f = file_object.path
        myfile = File(file_object)
        # myfile.open('rb').readlines()
        path = file_object.file.path
        with open(path, 'rb') as f:
            # Load excel workbook
            wb = load_workbook(f)
            ws = wb.active
            row_count = ws.max_row

            # a loop for scrape the excel file
            category = Category.objects.get(name='other')
            for i in range(2, 6):

                row = ws['A'+str(i):'M'+str(i)]

                test_object = Product(
                    name = ws['M' + str(i)].value,
                    stock = ws['L' + str(i)].value,
                    # author = ws['K' + str(i)].value,
                    # translator = ws['J' + str(i)].value,
                    price = ws['I' + str(i)].value,
                    publish_year = ws['H' + str(i)].value,
                    # edition = ws['G' + str(i)].value,
                    publisher = ws['F' + str(i)].value,
                    isbn = ws['E' + str(i)].value,
                    product_type = ws['D' + str(i)].value,
                    cover_type = ws['C' + str(i)].value,
                    barcode_number = ws['B' + str(i)].value,
                    size = ws['A' + str(i)].value,
                    category = category,
                )

                if test_object.barcode_number not in barcode_number_list:
                    test_object.save()

    return render(request,
                  'files/upload_database.html',
                  {'files': files,
                   'test_object': test_object
                   })
