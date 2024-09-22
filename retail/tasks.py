import decimal
import random
import logging
from io import BytesIO
from celery import shared_task
from django.core.mail import EmailMessage
from TestProject1 import settings
from .models import RetailObject
import qrcode


@shared_task
def clear_retail_debt_async(ids):
    RetailObject.objects.filter(id__in=ids).update(retail_debt=0)


@shared_task
def send_email_with_qr(retail_object_id, user_email):
    from .models import RetailObject
    retail_object = RetailObject.objects.get(id=retail_object_id)
    qr_data = f"Name: {retail_object.retail_name}\nEmail: {retail_object.retail_email}\n" \
              f"Country: {retail_object.retail_country}\nCity: {retail_object.retail_city}\n" \
              f"Street: {retail_object.retail_street}, Building: {retail_object.retail_building}"

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    email = EmailMessage(
        subject='Ваша контактная информация в QR-коде',
        body='Пожалуйста, найдите ваш QR-код с контактными данными.',
        from_email=settings.EMAIL_HOST_USER,
        to=[user_email],
    )

    buffer.seek(0)
    email.attach('qr_code.png', buffer.getvalue(), 'image/png')
    email.send()


@shared_task
def increase_debt():
    suppliers = RetailObject.objects.filter(retail_supplier__isnull=False)
    for supplier in suppliers:
        increase_amount = random.uniform(5, 500)
        supplier.retail_debt += decimal.Decimal(increase_amount)
        supplier.save()
        logging.info(f'Долг увеличен для {supplier.retail_name} с {increase_amount}.'
                     f' до: {supplier.retail_debt}.')


@shared_task
def decrease_debt():
    suppliers = RetailObject.objects.filter(retail_supplier__isnull=False)
    for supplier in suppliers:
        decrease_amount = random.uniform(100, 10000)
        supplier.retail_debt -= decimal.Decimal(decrease_amount)
        if supplier.retail_debt < 0:
            supplier.retail_debt = 0
        logging.info(f'Долг уменьшен {supplier.retail_name} с {decrease_amount}.'
                     f' до: {supplier.retail_debt}.')
        supplier.save()
