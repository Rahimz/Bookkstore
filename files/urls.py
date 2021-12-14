from django.urls import path, include
from . import views


urlpatterns = [
    path('upload/', views.add_to_database, name='upload_file'),
]
