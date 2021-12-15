from django.db import models


class File(models.Model):
    """
    This class is created for manual file upload to database.
    the file stores in media and help the admin to import it to database.
    """
    TYPE_CHOICES =[
        ('.excel','xls'),
        ('.pdf','pdf'),
    ]
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, unique=True, allow_unicode=True)
    file = models.FileField(upload_to='files/upload/')
    type = models.CharField(max_length=8,
                            choices=TYPE_CHOICES,
                            default='xls')
