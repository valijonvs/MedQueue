from django import forms
from django.utils import timezone

from .models import Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["patient_name", "phone_number", "doctor", "appointment_time"]
        labels = {
            "patient_name": "Bemor ismi",
            "phone_number": "Telefon raqami",
            "doctor": "Shifokorni tanlang",
            "appointment_time": "Kirish vaqtini tanlang",
        }
        widgets = {
            "patient_name": forms.TextInput(attrs={"placeholder": "Ism Familiya"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "+998 90 123 45 67"}),
            "appointment_time": forms.DateTimeInput(
                attrs={"type": "datetime-local", "placeholder": "2026-09-25T16:30"},
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def clean_appointment_time(self):
        appointment_time = self.cleaned_data.get("appointment_time")
        if appointment_time is None:
            raise forms.ValidationError("Kirish vaqti tanlanishi shart.")
        if appointment_time < timezone.now():
            raise forms.ValidationError("Kirish vaqti hozirgi vaqtdan keyin bo'lishi kerak.")
        return appointment_time
