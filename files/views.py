from django.shortcuts import render, get_object_or_404
from django.conf import settings

from .models import File


def add_to_database(request, file_slug=None):
    """
    This Function is designed to import datat from excel.
    The imported datat is very different, so we grab every files
    and check the headers and import file in a manual method.
    """
    files = File.objects.all()
    file_object = None
    if file_slug:
        file_object = get_object_or_404(File, slug=file_slug)

    return render(request,
                  'files/upload_database.html',
                  {'files': files,
                   'file_object': file_object})
