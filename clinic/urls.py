from django.urls import path

from .views import (
    advance_status_view,
    booking_view,
    cancel_appointment_view,
    doctor_advance_status_view,
    doctor_cancel_appointment_view,
    doctor_cabinet_view,
    doctor_login_view,
    doctor_logout_view,
    home_page,
    queue_view,
)

urlpatterns = [
    path("", home_page, name="home"),
    path("navbatga-yozilish/", booking_view, name="booking"),
    path("navbatlar/", queue_view, name="queue"),
    path("navbatlar/<int:pk>/keyingi-status/", advance_status_view, name="advance_status"),
    path("navbatlar/<int:pk>/bekor-qilish/", cancel_appointment_view, name="cancel_appointment"),
    path("kabinet/", doctor_cabinet_view, name="doctor_cabinet"),
    path("kabinet/kirish/", doctor_login_view, name="doctor_login"),
    path("kabinet/chiqish/", doctor_logout_view, name="doctor_logout"),
    path("kabinet/<int:pk>/keyingi-status/", doctor_advance_status_view, name="doctor_advance_status"),
    path("kabinet/<int:pk>/ochirish/", doctor_cancel_appointment_view, name="doctor_cancel_appointment"),
]
