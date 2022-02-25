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


def add_new_book_to_database_2(request, file_slug, check='check'):
    """
    to add new-book of the bookstore to datebase
    """

    duplicate_isbn = []
    isbn_error = []
    update_product = 0
    number_of_added_object = 0
    check_sum = 0
    price_change_list_ids = []
    product_updated_with_excel_ids = []
    new_book_to_update = []

    main_list_143 = []
    excel_isbn_in_db = []
    isbn_same_name_in_db = []
    different_name_with_same_isbn = []
    no_isbn_with_same_name_in_db = []
    excel_dic = []

    updated_product_to_keep_unchanged = Product.objects.filter(import_session__id='df0dca0d-4ba1-4b6f-b07a-8df5b8c3d121').values_list('isbn', flat=True)

    file_object = get_object_or_404(FileObject, slug=file_slug)

    myfile = File(file_object)

    path = file_object.file.path

    isbn_list = Product.objects.filter(available=True).exclude(import_session__id='df0dca0d-4ba1-4b6f-b07a-8df5b8c3d121').values_list('isbn', flat=True)
    name_list = Product.objects.filter(available=True).exclude(import_session__id='df0dca0d-4ba1-4b6f-b07a-8df5b8c3d121').values_list('name', flat=True)
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

            if page_number[0] == None:
                page_number = [0,]
            if price[0] == '----':
                price = [0,]


            # print(isbn[0])
            # print(len(isbn_list))
            if str(isbn[0]) not in updated_product_to_keep_unchanged:
                main_list_143.append(str(isbn[0]))
                # if str(isbn[0]) != 'None':
                database_product = Product.objects.filter(available=True).get(isbn=str(isbn[0]))
                # print('isbn in database', isbn[0], name[0])


                excel_isbn_in_db.append(str(isbn[0]))
                if name[0] == database_product.name:
                    if check == 'add':
                        database_product.stock += stock[0]
                        database_product.save()
                    # print('same isbn same name', isbn[0], name[0])
                    isbn_same_name_in_db.append(str(isbn[0]))
                else:
                    # print('different_name_with_same_isbn', isbn[0], name[0])
                    different_name_with_same_isbn.append(str(isbn[0]))
                    excel_dic.append((name[0], str(isbn[0]), stock[0]))

                    # new_book_to_update.append((isbn[0], name[0]))



            # # print(price, type(price))
            # # print(page_number, type(page_number))
            # if str(isbn[0])!='None' and (str(isbn[0]) in isbn_list):
            #     database_product = Product.objects.filter(available=True).get(isbn=str(isbn[0]))
            #
            #     if name[0] == database_product.name:
            #         product_updated_with_excel_ids.append(database_product.id)
            #         if price[0] != database_product.price:
            #             price_change_list_ids.append(database_product.id)
            #
            #
            #     if ws['B' + str(i)].value != database_product.name:
            #         duplicate_isbn.append((i, str(isbn[0]),ws['B' + str(i)].value, [Product.objects.filter(available=True).filter(isbn=str(isbn[0]))]))
            # else:
            #     if check == 'add':
            #         # print(name[0])
            #         product = Product.objects.create(
            #             name = name[0],
            #             isbn = str(isbn[0]),
            #             price = price[0],
            #             page_number =page_number[0],
            #             publisher = publisher[0],
            #             stock = stock[0],
            #             state = 'new',
            #             available = True,
            #             available_in_store = True,
            #             available_online = True,
            #             publish_year=None,
            #             import_session=current_import_session,
            #         )
            #         number_of_added_object += 1
            #         update_product += 1
            #

            if str(name[0]) in name_list:
                duplicate_isbn.append((i, str(isbn[0])))

            if len(str(isbn[0]))!= 13:
                isbn_error.append((i, str(isbn[0])))

    if check == 'add':
        current_import_session.quantity = number_of_added_object
        current_import_session.save()

    price_change_list = Product.objects.filter(pk__in=price_change_list_ids)
    product_updated_with_excel = Product.objects.filter(pk__in=product_updated_with_excel_ids)

    diff_name = Product.objects.filter(available=True).filter(isbn__in=different_name_with_same_isbn).order_by('isbn')
    # different_name_with_same_isbn = different_name_with_same_isbn.sort(key=lambda x:x[1])
    excel_dic = sorted(excel_dic, key=lambda x:x[1])

    print('should be as same as import session Q.',check_sum)
    print(len(updated_product_to_keep_unchanged) )
    # print(len(duplicate_isbn))
    # print(len(price_change_list))
    # print(len(product_updated_with_excel))
    # print(len(set(duplicate_isbn)))
    print('None' in updated_product_to_keep_unchanged)
    print('main_list_143: ', len(main_list_143))
    print('excel_dic: ', len(excel_dic))
    # print('excel_isbn_in_db: ', len(excel_isbn_in_db))
    # print('isbn_same_name_in_db: ', len(isbn_same_name_in_db))
    # print('different_name_with_same_isbn: ', len(different_name_with_same_isbn))
    print('no_isbn_with_same_name_in_db: ', len(no_isbn_with_same_name_in_db))
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
            'price_change_list': price_change_list,
            'product_updated_with_excel': product_updated_with_excel,

            'excel_isbn_in_db': excel_isbn_in_db,
            'isbn_same_name_in_db': isbn_same_name_in_db,
            'different_name_with_same_isbn': different_name_with_same_isbn,
            'no_isbn_with_same_name_in_db': no_isbn_with_same_name_in_db,
            'main_list_143': main_list_143,
            'diff_name': diff_name,
            'excel_dic': excel_dic,
         }
    )


def update_isbn_duplicate(request, product_isbn):
    pass


def name_correction(request, file_slug, check='check'):
    # variables
    updated_product_count = 0
    more_than_one = 0
    not_updated = []
    # excel file handle
    file_object = get_object_or_404(FileObject, slug=file_slug)

    myfile = File(file_object)

    path = file_object.file.path
    with open(path, 'rb') as f:
        # Load excel workbook
        wb = load_workbook(f)
        ws = wb.active
        row_count = ws.max_row

        # a loop for scrape the excel file
        # read the data in cells
        for i in range(2, row_count):

            row = ws['A'+str(i):'M'+str(i)]
            p_ex_id = ws['C' + str(i)].value,
            new_name = ws['F' + str(i)].value,


            try:
                database_product = Product.objects.get(pk=p_ex_id[0])
                if check == 'add':
                    updated_product_count +=1
                    database_product.name = new_name[0]
                    database_product.save()
            except:
                # print(p_ex_id[0], new_name[0])
                # print(new_name[0], type(new_name[0]))
                more_than_one +=1


    # print('updated_product_count', updated_product_count)
    # print('more_than_one', more_than_one)
    return render(
        request,
        'files/name_correction.html',
        {
            'file': myfile,
            'row_count': row_count,
            'updated_product_count': updated_product_count,
            'more_than_one': more_than_one,
         }
    )
