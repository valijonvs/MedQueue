import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clinic", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Appointment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("ticket_number", models.CharField(blank=True, editable=False, max_length=10, unique=True, verbose_name="Talon raqami")),
                ("patient_name", models.CharField(max_length=100, verbose_name="Bemor ismi")),
                ("phone_number", models.CharField(max_length=20, verbose_name="Telefon raqami")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Yozilgan vaqti")),
                (
                    "status",
                    models.CharField(
                        choices=[("kutilmoqda", "Kutilmoqda"), ("qabulda", "Qabulda"), ("yakunlandi", "Yakunlandi")],
                        default="kutilmoqda",
                        max_length=20,
                        verbose_name="Holati",
                    ),
                ),
                (
                    "doctor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="appointments",
                        to="clinic.doctor",
                        verbose_name="Shifokor",
                    ),
                ),
            ],
            options={
                "verbose_name": "Navbat yozuvi",
                "verbose_name_plural": "Navbat yozuvlari",
                "ordering": ["created_at"],
            },
        ),
    ]
