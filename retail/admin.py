from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from retail.models import *
from .tasks import clear_retail_debt_async


class WorkerInline(admin.TabularInline):
    model = RetailWorkers


class RetailObjectAdmin(admin.ModelAdmin):
    list_display = ['retail_type', 'retail_name', 'retail_debt', 'supplier_link', 'copy_email_button']
    list_filter = ['retail_country']
    actions = ['clear_debts']
    inlines = [WorkerInline]

    # Реализация пункта 1.3 (ссылка по кнопке на объект поставщика)
    def supplier_link(self, obj):
        if obj.retail_supplier:
            url = reverse('admin:retail_retailobject_change', args=[obj.retail_supplier.id])
            return format_html('<a href="{}">{}</a>', url, obj.retail_supplier)
        else:
            return None

    supplier_link.short_description = 'Поставщик'

    # Реализация пункта 1.3 и 2.2  (отчистка задолженности перед поставщиком)
    def clear_debts(self, request, queryset):
        if queryset.count() > 20:
            clear_retail_debt_async.delay(list(queryset.values_list('id', flat=True)))
            self.message_user(request, "Долговая задолженность успешно обнулена, выполняется асинхронно.")
        else:
            queryset.update(retail_debt=0)
            self.message_user(request, "Долговая задолженность успешно обнулена.")

    clear_debts.short_description = "Обнулить долговую задолженность продуктов"

    # Реализация задания 2.6 (кнопка скапоировать контакт с использованием JS)
    def copy_email_button(self, obj):
        return format_html(
            '<button class="copy-email-button" data-email="{}">Копировать email</button>',
            obj.retail_email
        )

    copy_email_button.short_description = 'Действие'

    class Media:
        js = ('js/copy_email.js',)


admin.site.register(Product)
admin.site.register(RetailObject, RetailObjectAdmin)
admin.site.register(UserToRetailObject)
