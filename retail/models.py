import datetime

from django.contrib.auth.models import User, AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from rest_framework.authtoken.models import Token as AuthToken


# Ниже реализуем модели из части 1, пункта 1, дополнительно подготавливаем основу для пункта 2:
class Country(models.Model):
    name = models.CharField(verbose_name='Название страны', max_length=50, unique=True)

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
    company_name = models.ForeignKey(ProductCompany, verbose_name='Компания изготовитель', on_delete=models.CASCADE)
    product_model = models.CharField(verbose_name='Модель', max_length=25)
    date_on_market = models.DateField(verbose_name='Дата выхода на рынок')

    class Meta:
        unique_together = ['company_name', 'product_model']
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    # Реализация валидации по длине модели (не длинее 25 символов) и дате выхода на рынок из задания 2.4:
    def clean(self):
        super().clean()
        if len(self.product_model) > 25:
            raise ValidationError("Название модели не может превышать 25 символов.")
        elif self.date_on_market > datetime.date.today():
            raise ValidationError("Проверьте дату выхода товара на рынок")

    def __str__(self):
        return self.product_model


# Ниже представлена реализация требований пункта 2, части 1
class RetailObject(models.Model):
    RETAIL_TYPE_CHOICES = [
        (0, 'Завод'),
        (1, 'Дистрибьютор'),
        (2, 'Дилерский центр'),
        (3, 'Крупная розничная сеть'),
        (4, 'Индивидуальный предприниматель')
    ]
    retail_type = models.IntegerField(verbose_name='Тип', choices=RETAIL_TYPE_CHOICES)
    retail_name = models.CharField(verbose_name='Название объекта', max_length=50)
    retail_email = models.EmailField()
    retail_country = models.ForeignKey(Country, verbose_name='Страна', on_delete=models.CASCADE)
    retail_city = models.CharField(verbose_name='Город', max_length=50)
    retail_street = models.CharField(verbose_name='Улица', max_length=50)
    retail_building = models.CharField(verbose_name='Номер здания', max_length=5)
    retail_products = models.ManyToManyField(Product, verbose_name='Товары', )
    retail_debt = models.DecimalField(verbose_name='Задолженность перед поставщиком',
                                      max_digits=100, decimal_places=2, default=0)
    retail_supplier = models.ForeignKey('self', verbose_name='Поставщик', null=True, blank=True,
                                        on_delete=models.SET_NULL,
                                        related_name='Поставщики')
    date_created = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)

    # Реализация валидации по длине объекта (не длинее 50 символов) сети из задания 2.4:
    def clean(self):
        super().clean()
        if len(self.retail_name) > 50:
            raise ValidationError("Название сети не может превышать 50 символов.")
        elif self.retail_debt < 0:
            raise ValidationError('Задолженность не может быть отрицательной')

    # Реализация иерархии постащик-реселлер
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


#Реализация задания 2.5, каждый пользователь привязывается к своей сети ретейла
class UserToRetailObject(models.Model):
    retail_object = models.ForeignKey(RetailObject, verbose_name='Точка ретейла', on_delete=models.CASCADE,
                                      blank=True, null=True)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = "Привязка пользователя к объекту"
        verbose_name_plural = "Привязки пользователя к объекту"
