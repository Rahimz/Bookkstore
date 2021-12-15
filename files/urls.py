from django.urls import path, include
from . import views


urlpatterns = [
    path('upload/', views.add_to_database, name='view_file'),
    path('upload/<slug:file_slug>/', views.add_to_database, name='upload_file'),
]
