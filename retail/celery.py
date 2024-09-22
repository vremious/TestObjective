import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TestProject1.settings')

app = Celery('retail')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.beat_schedule = {
    'increase_debt_every_3_hours': {
        'task': 'retail.tasks.increase_debt',
        'schedule': 3 * 60 * 60,
    },
    'decrease_debt_daily': {
        'task': 'retail.tasks.decrease_debt',
        'schedule': crontab(hour=6, minute=30),
    },
}
app.autodiscover_tasks(['retail'])
