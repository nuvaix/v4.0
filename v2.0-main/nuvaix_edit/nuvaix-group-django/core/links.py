"""Small helpers for WhatsApp / Google Play links."""
import re
from urllib.parse import quote

from django.conf import settings


def phone_digits(phone):
    """Normalise a phone number to international digits for wa.me links.

    '0803 123 4567' -> '2348031234567', '+234 803 123 4567' -> '2348031234567'.
    Returns '' when the number does not look usable.
    """
    digits = re.sub(r"\D", "", phone or "")
    if digits.startswith("00"):
        digits = digits[2:]
    if len(digits) == 11 and digits.startswith("0"):  # Nigerian local format
        digits = "234" + digits[1:]
    return digits if 7 <= len(digits) <= 15 else ""


def wa_url(number, text=""):
    url = f"https://wa.me/{number}"
    return f"{url}?text={quote(text)}" if text else url


def play_store_url(key=""):
    """Google Play link for a section ('paint', 'real-estate', ...), or '' if none is set."""
    k = (key or "").upper().replace("-", "_")
    url = settings.PLAY_STORE_URLS.get(k) or settings.PLAY_STORE_URL
    if not url:
        return ""
    if "play.google.com" in url and "referrer=" not in url:
        campaign = k.lower() or "general"
        referrer = f"utm_source=nuvaix_website&utm_medium=install_button&utm_campaign={campaign}"
        url += ("&" if "?" in url else "?") + "referrer=" + quote(referrer, safe="")
    return url
