from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Enquiry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(blank=True, max_length=40)),
                ("enquiry_type", models.CharField(
                    choices=[
                        ("general", "General enquiry"), ("technology", "Technology & IT"),
                        ("training", "Training"), ("paint", "NUVAIX Paint / bulk order"),
                        ("partnership", "Partnership"), ("careers", "Careers"), ("other", "Other"),
                    ],
                    default="general", max_length=24)),
                ("subject", models.CharField(max_length=180)),
                ("message", models.TextField(max_length=5000)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("status", models.CharField(
                    choices=[("new", "New"), ("in_progress", "In progress"), ("closed", "Closed")],
                    default="new", max_length=20)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
