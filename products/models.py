from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(max_length=250,
                            db_index=True,)
    slug = models.SlugField(max_length=300,
                            unique=True,
                            allow_unicode=True)


    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    # def get_absolute_url(self):
    #     return reverse('shop:product_list_by_category',
    #                    args=[self.slug])

    def __str__(self):
        return self.name


class Product(models.Model):
    STATE_CHOICES = [
        ('new', _('New')),
        ('used', _('Used')),
        ('children', _('children')),
    ]

    category = models.ForeignKey(Category,
                                 related_name='product',
                                 on_delete=models.CASCADE,)
    name = models.CharField(max_length=500, db_index=True)
    slug = models.SlugField(max_length=550, db_index=True, allow_unicode=True)

    barcode_number = models.CharField(max_length=13,
                                         blank=True, null=True)
    isbn = models.CharField(max_length=13,
                                         blank=True, null=True)

    image = models.ImageField(upload_to='products/images/',
                              blank=True)
    image_alt = models.CharField(max_length=300,
                                 blank=True,
                                 null=True)
    description = models.TextField(blank=True, null=True)
    stock = models.IntegerField(default=0)

    product_type = models.CharField(max_length=250,
                                  null=True, blank=True)

    state = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        choices=STATE_CHOICES
        )
    weight = models.FloatField(default=0,
                                 null=True, blank=True)
    size = models.CharField(max_length=250,
                            null=True, blank=True)
    cover_type = models.CharField(max_length=250,
                                  null=True, blank=True)

    publisher = models.CharField(max_length=250,
                                null=True, blank=True)
    publish_year = models.IntegerField(default=1400,
                                       validators=[MinValueValidator(1233),MaxValueValidator(1400)],
                                       null=True, blank=True)

    purchase_price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=0)

    available = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created',)
        index_together = (('id', 'slug'),)

    def get_absolute_url(self):
        return reverse('shop:product_detail',
                       args=[self.id, self.slug])
    def save(self, *args, **kwargs):
        if image and not self.image_alt:
            self.image_alt = self.name
    def __str__(self):
        return self.name
