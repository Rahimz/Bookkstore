from django.shortcuts import render, get_object_or_404
from django.conf import settings
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

from openpyxl import load_workbook
from io import BytesIO

from .models import File as FileObject, ImportSession
from django.core.files import File

from products.models import Product, Category


def list_of_files(request):
    files = FileObject.objects.all()
    return render(
        request,
        'files/list.html',
        {
        'files': files,
        }
    )


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

            # we make a label for each import session to  control it
            current_import_session = ImportSession.objects.create(user=request.user,)

            # read the data in cells
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
                    import_session=current_import_session,
                )

                if temp_object.barcode_number not in barcode_number_list:
                    try:
                        temp_object.save()
                        number_of_added_object += 1
                    except:
                        error_report[ws['M' + str(i)]] = ws['M' + str(i)].value
                        messages.error(request, 'Error updating your user details')



        current_import_session.quantity = number_of_added_object
        current_import_session.save()
    return render(request,
                  'files/upload_database.html',
                  {'files': files,
                   'number_of_added_object': number_of_added_object,
                   'error_report': error_report,
                   })


def add_new_book_to_database(request, file_slug, check='check'):
    """
    to add new-book of the bookstore to datebase
    """

    duplicate_isbn = []
    isbn_error = []
    update_product = 0
    number_of_added_object = 0

    file_object = get_object_or_404(FileObject, slug=file_slug)

    myfile = File(file_object)

    path = file_object.file.path

    isbn_list = Product.objects.filter(isbn__isnull=False).values_list('isbn', flat=True)
    name_list = Product.objects.values_list('name', flat=True)
    barcode_number_list = Product.objects.filter(barcode_number__isnull=False).values_list('barcode_number', flat=True)

    if check == 'add':

        # we make a label for each import session to  control it
        current_import_session = ImportSession.objects.create(user=request.user,)

    with open(path, 'rb') as f:
        # Load excel workbook
        wb = load_workbook(f)
        ws = wb.active
        row_count = ws.max_row

        # a loop for scrape the excel file
        # read the data in cells
        for i in range(2, row_count):

            row = ws['A'+str(i):'M'+str(i)]
            name = ws['B' + str(i)].value,
            isbn = ws['C' + str(i)].value,
            price = ws['D' + str(i)].value if not None else (0,),
            page_number = ws['E' + str(i)].value,
            publisher = ws['F' + str(i)].value,
            stock = ws['G' + str(i)].value,

            if page_number[0] == '':
                page_number = [0,]
            if price[0] == '----':
                price = [0,]


            if check == 'add':
                product = Product.objects.create(
                    name = name[0],
                    isbn = str(isbn[0]),
                    price = price[0],
                    page_number =page_number[0],
                    publisher = publisher[0],
                    stock = stock[0],
                    state = 'new',
                    available = True,
                    available_in_store = True,
                    available_online = True,
                    import_session=current_import_session,
                )
                number_of_added_object += 1
                update_product += 1

            # print(price, type(price))
            # print(page_number, type(page_number))
            if str(isbn[0]) in isbn_list:
                duplicate_isbn.append((i, str(isbn[0])))

            if str(name[0]) in name_list:
                duplicate_isbn.append((i, str(isbn[0])))

            if len(str(isbn[0]))!= 13:
                isbn_error.append((i, str(isbn[0])))


    current_import_session.quantity = number_of_added_object
    current_import_session.save()

    # print(len(duplicate_isbn))
    # print(len(set(duplicate_isbn)))
    return render(
        request,
        'files/check_update.html',
        {
            'file': myfile,
            # 'number_of_added_object': number_of_added_object,
            # 'error_report': error_report,
            'isbn_list': isbn_list,
            'isbn_error': isbn_error,
            'duplicate_isbn': duplicate_isbn,
            'row_count': row_count,
            'update_product': update_product,
         }
    )
