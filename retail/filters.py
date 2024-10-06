from django.db.models import Avg
from django_filters import rest_framework as filters

from .models import RetailObject


# Реализация фильтрации по размеру долга и по названию страны с продуктами
class ModelFilter(filters.FilterSet):
    average_field = filters.BooleanFilter(field_name='Долг выше среднего', method='filter_by_average',
                                          label='Долг выше среднего')

    def filter_by_average(self, queryset, name, value):
        average_value = RetailObject.objects.aggregate(Avg('retail_debt'))['retail_debt__avg']
        if value is True:
            return queryset.filter(retail_debt__gt=average_value)
        elif value is False:
            return queryset.filter(retail_debt__lt=average_value)
        else:
            return queryset

    class Meta:
        model = RetailObject
        fields = ['retail_products', 'retail_country__name']
