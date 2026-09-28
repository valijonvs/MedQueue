from django.contrib import admin

from .models import Appointment, Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "specialty", "room_number", "phone_number", "user")
    list_filter = ("specialty",)
    search_fields = ("first_name", "last_name", "phone_number")
    ordering = ("last_name", "first_name")
    list_per_page = 25
    autocomplete_fields = ("user",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("ticket_number", "patient_name", "doctor", "status", "created_at")
    list_filter = ("status", "doctor")
    search_fields = ("patient_name", "phone_number", "ticket_number")
    ordering = ("-created_at",)
    list_per_page = 25
