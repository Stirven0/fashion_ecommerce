from django.conf import settings


def store_settings(request):
    return {
        "store_name": settings.STORE_NAME,
        "store_whatsapp": settings.STORE_WHATSAPP,
        "store_email": settings.STORE_EMAIL,
        "store_address": settings.STORE_ADDRESS,
        "store_currency": settings.STORE_CURRENCY,
    }
