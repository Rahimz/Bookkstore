from django.db import models


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
    category = models.ForeignKey(Category,
                                 related_name='product',
                                 on_delete=models.CASCADE,)
    name = models.CharField(max_length=500, db_index=True)
    slug = models.SlugField(max_length=550, db_index=True, allow_unicode=True)
    image = models.ImageField(upload_to='products/images/',
                              blank=True)
    image_alt = models.CharField(max_length=300,
                                 blank=True,
                                 null=True)
    short_description = models.CharField(max_length=250,
                                         default='',
                                         blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    stock = models.IntegerField(default=0)
    weight = models.FloatField(default=0,
                                 null=True, blank=True)
    available = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created',)
        index_together = (('id', 'slug'),)

    def get_absolute_url(self):
        return reverse('shop:product_detail',
                       args=[self.id, self.slug])

    def __str__(self):
        return self.name
