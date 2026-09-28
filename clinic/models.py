from django.conf import settings
from django.db import models
from django.utils import timezone


class Doctor(models.Model):
    class Specialty(models.TextChoices):
        STOMATOLOG = "stomatolog", "Stomatolog"
        TERAPEVT = "terapevt", "Terapevt"
        KARDIOLOG = "kardiolog", "Kardiolog"
        PEDIATR = "pediatr", "Pediatr"

    # Shifokor shaxsiy kabinetiga faqat shu foydalanuvchi hisobi bilan kira oladi.
    # null=True — chunki ba'zi shifokorlarga hali login/parol biriktirilmagan bo'lishi mumkin.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="Foydalanuvchi hisobi",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="doctor_profile",
    )
    first_name = models.CharField("Ism", max_length=100)
    last_name = models.CharField("Familiya", max_length=100)
    specialty = models.CharField(
        "Mutaxassislik",
        max_length=20,
        choices=Specialty.choices,
        default=Specialty.TERAPEVT,
    )
    room_number = models.PositiveSmallIntegerField("Xona raqami")
    phone_number = models.CharField("Telefon raqami", max_length=20)

    class Meta:
        verbose_name = "Shifokor"
        verbose_name_plural = "Shifokorlar"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.get_specialty_display()})"


class Appointment(models.Model):
    class Status(models.TextChoices):
        KUTILMOQDA = "kutilmoqda", "Kutilmoqda"
        QABULDA = "qabulda", "Qabulda"
        YAKUNLANDI = "yakunlandi", "Yakunlandi"

    # Ketma-ketlik: har bir status keyingisiga shu tartibda o'tadi
    STATUS_ORDER = [Status.KUTILMOQDA, Status.QABULDA, Status.YAKUNLANDI]

    ticket_number = models.CharField(
        "Talon raqami", max_length=10, unique=True, blank=True, editable=False
    )
    patient_name = models.CharField("Bemor ismi", max_length=100)
    phone_number = models.CharField("Telefon raqami", max_length=20)
    doctor = models.ForeignKey(
        Doctor,
        verbose_name="Shifokor",
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    created_at = models.DateTimeField("Yozilgan vaqti", auto_now_add=True)
    appointment_time = models.DateTimeField(
        "Kirish vaqti",
        default=timezone.now,
        help_text="Bemor tanlagan kelish vaqti",
    )
    status = models.CharField(
        "Holati",
        max_length=20,
        choices=Status.choices,
        default=Status.KUTILMOQDA,
    )

    class Meta:
        verbose_name = "Navbat yozuvi"
        verbose_name_plural = "Navbat yozuvlari"
        ordering = ["appointment_time", "created_at"]

    def __str__(self):
        return f"{self.ticket_number} - {self.patient_name} ({self.doctor})"

    def save(self, *args, **kwargs):
        # Talon raqami faqat birinchi marta saqlashda avtomatik yaratiladi (DR-01, DR-02, ...)
        if not self.ticket_number:
            oxirgi_raqam = Appointment.objects.count() + 1
            self.ticket_number = f"DR-{oxirgi_raqam:02d}"
        super().save(*args, **kwargs)

    def keyingi_statusga_otish(self):
        # Statusni navbat bo'yicha keyingisiga o'zgartiradi: Kutilmoqda -> Qabulda -> Yakunlandi
        joriy_index = self.STATUS_ORDER.index(self.status)
        agar_oxirgi_emas = joriy_index < len(self.STATUS_ORDER) - 1
        if agar_oxirgi_emas:
            self.status = self.STATUS_ORDER[joriy_index + 1]
