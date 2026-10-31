from django.db import migrations, models

DELIVERY = [
    ("skipped", "Not requested"), ("sent", "Delivered"),
    ("manual", "Customer sends manually"), ("failed", "Failed"),
]


class Migration(migrations.Migration):
    dependencies = [("core", "0001_initial")]
    operations = [
        migrations.AddField(model_name="enquiry", name="channels",
                            field=models.CharField(default="whatsapp", max_length=40)),
        migrations.AddField(model_name="enquiry", name="whatsapp_status",
                            field=models.CharField(choices=DELIVERY, default="skipped", max_length=12)),
        migrations.AddField(model_name="enquiry", name="email_status",
                            field=models.CharField(choices=DELIVERY, default="skipped", max_length=12)),
        migrations.AddField(model_name="enquiry", name="delivery_note",
                            field=models.TextField(blank=True, default="")),
        migrations.AlterField(
            model_name="enquiry", name="enquiry_type",
            field=models.CharField(
                choices=[
                    ("general", "General enquiry"), ("technology", "Technology & IT"),
                    ("training", "Training"), ("paint", "NUVAIX Paint / bulk order"),
                    ("partnership", "Partnership"), ("careers", "Careers"), ("other", "Other"),
                    ("construction", "Construction & Engineering"), ("real_estate", "Real Estate & Property"),
                    ("automobile", "Automobile Services"), ("logistics", "Logistics & Supply Chain"),
                    ("manufacturing", "Manufacturing & Industrial"), ("healthcare", "Healthcare & Medicine"),
                    ("retail_agriculture", "Retail & Agriculture"), ("consultancy", "Consultancy Services"),
                    ("investment", "Investments & Venture Development"), ("mobile_app", "NUVAIX Android app"),
                ],
                default="general", max_length=24),
        ),
    ]
