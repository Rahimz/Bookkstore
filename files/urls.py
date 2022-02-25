from django.urls import path, include
from . import views

app_name = 'files'

urlpatterns = [
    path('list/', views.list_of_files, name='list_of_files'),
    path('upload/', views.add_to_database, name='view_file'),
    path('upload/<slug:file_slug>/', views.add_to_database, name='upload_file'),

    path('upload/new-product/<slug:file_slug>/<str:check>/', views.add_new_book_to_database, name='add_new_book_to_database_check'),
    path('upload/new-product/<slug:file_slug>/', views.add_new_book_to_database, name='add_new_book_to_database'),

    path('upload/new-product-2/<slug:file_slug>/<str:check>/', views.add_new_book_to_database_2, name='add_new_book_to_database_check_2'),
    path('upload/new-product-2/<str:product_isbn>/<int:quantity>/', views.update_isbn_duplicate, name='update_isbn_duplicate'),

    path('upload/name-correction/<slug:file_slug>/<str:check>/', views.name_correction, name='name_correction'),

    path('upload/correction_140/<slug:file_slug>/<str:check>/', views.correction_140, name='correction_140'),

    path('upload/new-product-3/<slug:file_slug>/<str:check>/', views.add_new_book_to_database_3, name='add_new_book_to_database_3'),
]
