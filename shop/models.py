from django.db import models



class Slogan(models.Model):
    slogan = models.CharField(
        max_length=350
    )
    author = models.CharField(
        max_length=100,
        default=''
    )
    active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.author} {self.slogan[0:15]}"
