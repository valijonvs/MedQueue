from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.utils import timezone

from .forms import AppointmentForm
from .models import Appointment, Doctor


class AppointmentBookingTimeTests(TestCase):
    def setUp(self):
        self.doctor = Doctor.objects.create(
            first_name="Nodir",
            last_name="Rahimov",
            specialty=Doctor.Specialty.TERAPEVT,
            room_number=12,
            phone_number="+998991234567",
        )

    def test_form_accepts_selected_appointment_time(self):
        future_time = timezone.now() + timedelta(days=1)
        form = AppointmentForm(
            data={
                "patient_name": "Ali Valiev",
                "phone_number": "+998901234567",
                "doctor": self.doctor.pk,
                "appointment_time": future_time.strftime("%Y-%m-%dT%H:%M"),
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        appointment = form.save()
        self.assertEqual(
            appointment.appointment_time.strftime("%Y-%m-%dT%H:%M"),
            future_time.strftime("%Y-%m-%dT%H:%M"),
        )

    def test_doctor_cabinet_shows_all_appointments(self):
        User = get_user_model()
        user = User.objects.create_user(username="doctor_user", password="secret123")
        doctor = Doctor.objects.create(
            user=user,
            first_name="Doctor",
            last_name="User",
            specialty=Doctor.Specialty.TERAPEVT,
            room_number=5,
            phone_number="+998991112233",
        )

        future_time = timezone.now() + timedelta(days=2, hours=3)
        appointment = Appointment.objects.create(
            patient_name="Sardor",
            phone_number="+998909876543",
            doctor=doctor,
            appointment_time=future_time,
        )

        client = Client()
        self.assertTrue(client.login(username="doctor_user", password="secret123"))

        response = client.get("/kabinet/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, appointment.patient_name)

    def test_queue_page_displays_all_queue_records(self):
        future_time = timezone.now() + timedelta(days=3)
        doctor = Doctor.objects.create(
            first_name="Ali",
            last_name="Valiyev",
            specialty=Doctor.Specialty.TERAPEVT,
            room_number=10,
            phone_number="+998935554433",
        )
        appointment = Appointment.objects.create(
            patient_name="Test Bemor",
            phone_number="+998901112233",
            doctor=doctor,
            appointment_time=future_time,
        )

        response = self.client.get("/navbatlar/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, appointment.patient_name)
