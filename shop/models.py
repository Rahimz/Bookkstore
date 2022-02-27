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


class Note(models.Model):
    title = models.CharField(
        max_length=120,
    )
    body = models.TextField()
    create = models.DateTimeField(
        auto_now_add=True
    )
    active = models.BooleanField(
        default=True
    )
    tag = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    def __str__(self):
        return self.title
