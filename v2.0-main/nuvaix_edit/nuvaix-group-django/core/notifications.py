"""Deliver website enquiries to the NUVAIX team via WhatsApp group and/or email."""
import json
import logging
import urllib.error
import urllib.request

from django.conf import settings
from django.core.mail import EmailMessage

from .links import phone_digits, wa_url

log = logging.getLogger(__name__)


def reference(enq):
    return f"NX-{enq.pk:05d}"


def _type_label(enq):
    return dict(enq.ENQUIRY_TYPES).get(enq.enquiry_type, enq.enquiry_type)


def team_text(enq, whatsapp=False):
    """The message the NUVAIX team sees (in the WhatsApp group or in their inbox)."""
    b = (lambda s: f"*{s}*") if whatsapp else (lambda s: s)
    lines = [
        b(f"New website enquiry {reference(enq)}"),
        f"{b('Type:')} {_type_label(enq)}",
        f"{b('Name:')} {enq.name}",
        f"{b('Email:')} {enq.email}",
    ]
    digits = phone_digits(enq.phone)
    if enq.phone:
        lines.append(f"{b('Phone:')} {enq.phone}")
    if digits:
        lines.append(f"{b('Reply on WhatsApp:')} https://wa.me/{digits}")
    lines += [f"{b('Subject:')} {enq.subject}", "", enq.message]
    return "\n".join(lines)


def customer_prefill_text(enq):
    """Pre-written WhatsApp message for the customer's own phone (manual fallback)."""
    text = (
        f"Hello NUVAIX GROUP, I'm {enq.name}. ({reference(enq)})\n"
        f"Enquiry type: {_type_label(enq)}\nSubject: {enq.subject}\n\n{enq.message}"
    )
    if enq.phone:
        text += f"\n\nPhone: {enq.phone}"
    return text[:1500]


def customer_whatsapp_url(enq):
    return wa_url(settings.WHATSAPP_NUMBER, customer_prefill_text(enq))


def customer_mailto_url(enq):
    if not settings.NUVAIX_EMAIL:
        return ""
    from urllib.parse import quote
    subject = quote(f"[{reference(enq)}] {enq.subject}")
    body = quote(customer_prefill_text(enq))
    return f"mailto:{settings.NUVAIX_EMAIL}?subject={subject}&body={body}"


def send_whatsapp_group(enq):
    """Post the enquiry into the NUVAIX WhatsApp group through the configured gateway.

    Returns (status, note): "sent", "manual" (gateway not configured) or "failed".
    """
    token, group = settings.WHATSAPP_GATEWAY_TOKEN, settings.WHATSAPP_GROUP_ID
    if not (token and group):
        return "manual", "WhatsApp gateway not configured; customer was offered the wa.me link."
    to = group if "@" in group else f"{group}@g.us"
    payload = json.dumps({"to": to, "body": team_text(enq, whatsapp=True)}).encode("utf-8")
    request = urllib.request.Request(
        settings.WHATSAPP_GATEWAY_URL,
        data=payload,
        method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            if 200 <= response.status < 300:
                return "sent", ""
            return "failed", f"Gateway returned HTTP {response.status}"
    except urllib.error.HTTPError as exc:
        log.warning("WhatsApp gateway HTTP error %s for %s", exc.code, reference(enq))
        return "failed", f"Gateway returned HTTP {exc.code}"
    except (urllib.error.URLError, OSError, ValueError) as exc:
        log.warning("WhatsApp gateway unreachable for %s: %s", reference(enq), exc)
        return "failed", f"Gateway unreachable: {exc}"


def send_team_email(enq):
    """Email the enquiry to NUVAIX_EMAIL (Reply-To = customer). Returns (status, note)."""
    if not settings.NUVAIX_EMAIL:
        return "skipped", "NUVAIX_EMAIL is not set."
    if not settings.EMAIL_CONFIGURED:
        return "skipped", "Email (SMTP) is not configured."
    subject = " ".join(f"[{reference(enq)}] {enq.subject}".split())
    try:
        EmailMessage(
            subject=subject,
            body=team_text(enq),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.NUVAIX_EMAIL],
            reply_to=[enq.email],
        ).send(fail_silently=False)
    except Exception as exc:  # SMTP/network errors must never break the customer's submission
        log.warning("Enquiry email failed for %s: %s", reference(enq), exc)
        return "failed", f"Email failed: {exc}"
    return "sent", ""


def deliver(enq):
    """Send the enquiry through every channel the customer chose and record the outcome."""
    channels = [c for c in enq.channels.split(",") if c]
    notes = []
    if "whatsapp" in channels:
        enq.whatsapp_status, note = send_whatsapp_group(enq)
        notes.append(note)
    else:
        enq.whatsapp_status = "skipped"
    if "email" in channels:
        enq.email_status, note = send_team_email(enq)
        notes.append(note)
    else:
        enq.email_status = "skipped"
    enq.delivery_note = " | ".join(n for n in notes if n)[:1000]
    enq.save(update_fields=["whatsapp_status", "email_status", "delivery_note"])
    return enq
