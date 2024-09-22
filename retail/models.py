from django.core.exceptions import ValidationError
from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"


class ProductCompany(models.Model):
    company_name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"

    def __str__(self):
        return self.company_name


class Product(models.Model):
    company_name = models.ForeignKey(ProductCompany, on_delete=models.CASCADE)
    product_model = models.CharField(max_length=50)
    date_on_market = models.DateField()

    class Meta:
        unique_together = ['company_name', 'product_model']
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return self.product_model


class RetailObject(models.Model):
    RETAIL_TYPE = [
        (0, 'Завод'),
        (1, 'Дистрибьютор'),
        (2, 'Дилерский центр'),
        (3, 'Крупная розничная сеть'),
        (4, 'Индивидуальный предприниматель')
    ]
    retail_type = models.IntegerField(verbose_name='Тип', choices=RETAIL_TYPE)
    retail_name = models.CharField(verbose_name='Название объекта', max_length=50)
    retail_email = models.EmailField()
    retail_country = models.ForeignKey(Country, verbose_name='Страна', on_delete=models.CASCADE)
    retail_city = models.CharField(verbose_name='Город', max_length=50)
    retail_street = models.CharField(verbose_name='Улица', max_length=50)
    retail_building = models.CharField(verbose_name='Номер здания', max_length=5)
    retail_products = models.ManyToManyField(Product, verbose_name='Товары', )
    retail_debt = models.DecimalField(verbose_name='Задолженность перед поставщиком',
                                      max_digits=100, decimal_places=2, default=0.00)
    retail_supplier = models.ForeignKey('self', verbose_name='Поставщик', null=True, blank=True,
                                        on_delete=models.SET_NULL,
                                        related_name='Поставщики')
    date_created = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)

    def clean(self):
        super().clean()
        if len(self.retail_name) > 50:
            raise ValidationError("Название сети не может превышать 50 символов.")

    def save(self, *args, **kwargs):
        if self.retail_supplier and self.retail_type <= self.retail_supplier.retail_type < 4:
            self.retail_type = self.retail_supplier.retail_type + 1
        elif self.retail_supplier and self.retail_supplier.retail_type < self.retail_type:
            pass
        elif not self.retail_supplier:
            self.retail_type = 0
        else:
            self.retail_type = 4
        super().save(*args, **kwargs)

    def get_workers(self):
        return self.retailworkers_set.all()

    def __str__(self):
        return f'{self.retail_name}'

    class Meta:
        verbose_name = "Точка ретейла"
        verbose_name_plural = "Точки ретейла"


class RetailWorkers(models.Model):
    retail_object = models.ForeignKey(RetailObject, on_delete=models.CASCADE)
    worker_surname_name = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
