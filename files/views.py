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
    if file_slug:
        file_object = get_object_or_404(FileObject, slug=file_slug)
        # f = file_object.path
        myfile = File(file_object)
        # myfile.open('rb').readlines()
        path = file_object.file.path
        with open(path, 'rb') as f:
            wb = load_workbook(f)
            ws = wb.active
            row = ws['A2':'M2']
            category = Category.objects.get(name='other')
            # category1 = Category()
            # category1.name = 'test1'
            # category1.slug = 'test1'
            # category1.save()
            test_object = Product.objects.create(
                name = ws['M2'].value,
                stock = ws['L2'].value,
                # author = ws['K2'].value,
                # translator = ws['J2'].value,
                price = ws['I2'].value,
                publish_year = ws['H2'].value,
                # edition = ws['G2'].value,
                publisher = ws['F2'].value,
                isbn = ws['E2'].value,
                product_type = ws['D2'].value,
                cover_type = ws['C2'].value,
                barcode_number = ws['B2'].value,
                size = ws['A2'].value,
                category = category,
            )
            # test_object.name = ws['M2'].value
            # test_object.stock = ws['L2'].value
            # test_object.author = ws['K2'].value
            # test_object.translator = ws['J2'].value
            # test_object.price = ws['I2'].value
            # test_object.publicationYear = ws['H2'].value
            # test_object.edition = ws['G2'].value
            # test_object.publication = ws['F2'].value
            # test_object.isbn = ws['E2'].value
            # test_object.prductType = ws['D2'].value
            # test_object.coverType = ws['C2'].value
            # test_object.barCode = ws['B2'].value
            # test_object.size = ws['A2'].value
            # test_object.category = category
            # test_object.save()
        # myfile.close()
    return render(request,
                  'files/upload_database.html',
                  {'files': files,
                   'test_object': test_object
                   })
