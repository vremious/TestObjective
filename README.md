Тестовое задание RocketData на позицию Junior+ Python Developer от Емельянова Дениса Андреевича.

Сделаны все задания

Все необходимые зависимости в requirements.txt

Из дополнительного - необходим действующий сервер (или контейнер) с Redis
для реализации функционала Celery и Celery Beat.

Я Docker Desktop с контейнером Redis[latest]

Перед проверкой функционала необходимо поменять в Settings:
CELERY_BROKER_URL = 'redis://localhost:6379/0'

CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

EMAIL_HOST = 'smtp.your-email-provider.com'

EMAIL_PORT = 587

EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'your-email@example.com'

EMAIL_HOST_PASSWORD = 'your-email-password'