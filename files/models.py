from django.db import models


class File(models.Model):
    TYPE_CHOICES =[
        ('.excel','xls'),
        ('.pdf','pdf'),
    ]
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to='media/files/upload/')
    type = models.CharField(max_length=8,
                            choices=TYPE_CHOICES,
                            default='xls')
