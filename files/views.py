from django.shortcuts import render, get_object_or_404
from django.conf import settings
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

from openpyxl import load_workbook
from io import BytesIO

from .models import File as FileObject
from django.core.files import File

from products.models import Product, Category


@staff_member_required
def add_to_database(request, file_slug=None):
    """
    This Function is designed to import datat from excel.
    The imported datat is very different, so we grab every files
    and check the headers and import file in a manual method.
    """
    files = FileObject.objects.all()

    file_object = None
    row = None
    temp_object = None

    # use for reports
    number_of_added_object = 0

    # erroe report
    error_report = {}

    # grab a list of available barcode numbers
    barcode_number_list =Product.objects.all().values_list('barcode_number', flat=True)
    if file_slug:
        file_object = get_object_or_404(FileObject, slug=file_slug)

        myfile = File(file_object)

        path = file_object.file.path
        with open(path, 'rb') as f:
            # Load excel workbook
            wb = load_workbook(f)
            ws = wb.active
            row_count = ws.max_row

            # a loop for scrape the excel file
            category = Category.objects.get(name='other')

            for i in range(2, row_count):

                row = ws['A'+str(i):'M'+str(i)]

                temp_object = Product(
                    name = ws['M' + str(i)].value,
                    stock = ws['L' + str(i)].value,
                    author = ws['K' + str(i)].value,
                    translator = ws['J' + str(i)].value,
                    price = ws['I' + str(i)].value,
                    publish_year = ws['H' + str(i)].value,
                    edition = ws['G' + str(i)].value,
                    publisher = ws['F' + str(i)].value,
                    isbn = ws['E' + str(i)].value,
                    product_type = ws['D' + str(i)].value,
                    cover_type = ws['C' + str(i)].value,
                    barcode_number = ws['B' + str(i)].value,
                    size = ws['A' + str(i)].value,
                    category = category,
                )

                if temp_object.barcode_number not in barcode_number_list:
                    try:
                        temp_object.save()
                        number_of_added_object += 1
                    except:
                        error_report[ws['M' + str(i)]] = ws['M' + str(i)].value
                        messages.error(request, 'Error updating your profile')




    return render(request,
                  'files/upload_database.html',
                  {'files': files,
                   'number_of_added_object': number_of_added_object,
                   'error_report': error_report,
                   })
