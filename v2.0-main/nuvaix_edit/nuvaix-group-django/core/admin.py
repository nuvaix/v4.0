from django.contrib import admin, messages
from django.utils.html import format_html

from .links import phone_digits
from .models import Enquiry
from .notifications import deliver


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "enquiry_type", "channels", "whatsapp_status", "email_status", "status", "created_at", "reply")
    list_filter = ("status", "enquiry_type", "whatsapp_status", "email_status", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("created_at", "whatsapp_status", "email_status", "delivery_note")
    list_editable = ("status",)
    actions = ["resend_notifications"]

    @admin.display(description="Reply")
    def reply(self, obj):
        links = []
        digits = phone_digits(obj.phone)
        if digits:
            links.append(format_html('<a href="https://wa.me/{}" target="_blank" rel="noopener">WhatsApp</a>', digits))
        links.append(format_html('<a href="mailto:{}">Email</a>', obj.email))
        return format_html(" · ".join("{}" for _ in links), *links)

    @admin.action(description="Re-send selected enquiries to WhatsApp group / email")
    def resend_notifications(self, request, queryset):
        for enquiry in queryset:
            deliver(enquiry)
        self.message_user(request, f"Re-sent {queryset.count()} enquiry(ies). Check the status columns.", messages.INFO)
