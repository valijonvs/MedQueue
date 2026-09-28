import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("clinic", "0002_appointment"),
    ]

    operations = [
        migrations.AddField(
            model_name="doctor",
            name="user",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="doctor_profile",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Foydalanuvchi hisobi",
            ),
        ),
    ]
