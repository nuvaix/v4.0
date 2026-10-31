from django.db import models


class Enquiry(models.Model):
    ENQUIRY_TYPES = [
        ("general", "General enquiry"), ("technology", "Technology & IT"),
        ("training", "Training"), ("paint", "NUVAIX Paint / bulk order"),
        ("partnership", "Partnership"), ("careers", "Careers"), ("other", "Other"),
        ("construction", "Construction & Engineering"), ("real_estate", "Real Estate & Property"),
        ("automobile", "Automobile Services"), ("logistics", "Logistics & Supply Chain"),
        ("manufacturing", "Manufacturing & Industrial"), ("healthcare", "Healthcare & Medicine"),
        ("retail_agriculture", "Retail & Agriculture"), ("consultancy", "Consultancy Services"),
        ("investment", "Investments & Venture Development"), ("mobile_app", "NUVAIX Android app"),
    ]
    DELIVERY_STATUSES = [
        ("skipped", "Not requested"), ("sent", "Delivered"),
        ("manual", "Customer sends manually"), ("failed", "Failed"),
    ]
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    enquiry_type = models.CharField(max_length=24, choices=ENQUIRY_TYPES, default="general")
    subject = models.CharField(max_length=180)
    message = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[("new", "New"), ("in_progress", "In progress"), ("closed", "Closed")], default="new")
    # Which channels the customer chose: comma separated subset of "whatsapp,email".
    channels = models.CharField(max_length=40, default="whatsapp")
    whatsapp_status = models.CharField(max_length=12, choices=DELIVERY_STATUSES, default="skipped")
    email_status = models.CharField(max_length=12, choices=DELIVERY_STATUSES, default="skipped")
    delivery_note = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} - {self.name}"
