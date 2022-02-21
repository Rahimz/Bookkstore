from django.urls import path, include
from . import views


urlpatterns = [
    path('list/', views.list_of_files, name='list_of_files'),
    path('upload/', views.add_to_database, name='view_file'),
    path('upload/<slug:file_slug>/', views.add_to_database, name='upload_file'),

    path('upload/new-product/<slug:file_slug>/<str:check>/', views.add_new_book_to_database, name='add_new_book_to_database_check'),
    path('upload/new-product/<slug:file_slug>/', views.add_new_book_to_database, name='add_new_book_to_database'),
]
