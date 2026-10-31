from django.conf import settings

from .links import play_store_url
from .models import Enquiry


def site_choices(request):
    return {
        "enquiry_choices": Enquiry.ENQUIRY_TYPES,
        "site": {
            "wa_number": settings.WHATSAPP_NUMBER,
            "wa_display": settings.WHATSAPP_DISPLAY,
            "email": settings.NUVAIX_EMAIL,
            "play_store_url": play_store_url(""),
        },
    }
