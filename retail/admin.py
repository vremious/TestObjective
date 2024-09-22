from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .tasks import clear_retail_debt_async
from retail.models import *


class WorkerInline(admin.TabularInline):
    model = RetailWorkers


class RetailObjectAdmin(admin.ModelAdmin):
    list_display = ['retail_type', 'retail_name', 'retail_debt', 'supplier_link']
    list_filter = ['retail_country']
    actions = ['clear_debts']
    inlines = [WorkerInline]

    def supplier_link(self, obj):
        if obj.retail_supplier:
            url = reverse('admin:retail_retailobject_change', args=[obj.retail_supplier.id])
            return format_html('<a href="{}">{}</a>', url, obj.retail_supplier)
        else:
            return None

    supplier_link.short_description = 'Supplier'

    def clear_debts(self, request, queryset):
        if queryset.count() > 20:
            clear_retail_debt_async.delay(list(queryset.values_list('id', flat=True)))
            self.message_user(request, "Долговая задолженность успешно обнулена, выполняется асинхронно.")
        else:
            queryset.update(retail_debt=0)
            self.message_user(request, "Долговая задолженность успешно обнулена.")

    clear_debts.short_description = "Обнулить долговую задолженность продуктов"


# admin.site.register(Country)
# admin.site.register(ProductCompany)
admin.site.register(Product)
admin.site.register(RetailObject, RetailObjectAdmin)
# admin.site.register(RetailWorkers)
