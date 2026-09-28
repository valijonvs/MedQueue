from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import AppointmentForm
from .models import Appointment, Doctor


def home_page(request):
    return render(request, "clinic/home.html")


def booking_view(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save()
            messages.success(
                request,
                f"Siz navbatga muvaffaqiyatli yozildingiz! Talon: {appointment.ticket_number}. Kelish vaqti: {appointment.appointment_time.strftime('%d.%m.%Y %H:%M')}",
            )
            return redirect("booking")
    else:
        form = AppointmentForm()

    return render(request, "clinic/booking.html", {"form": form})


def bugungi_statistika(appointments_qs):
    # Bitta querysetdan holatlar bo'yicha sonlarni hisoblab beradi (ressepshen va shifokor
    # kabinetida bir xil statistik kartochkalarni ko'rsatish uchun ishlatiladi)
    return {
        "jami": appointments_qs.count(),
        "kutilmoqda": appointments_qs.filter(status=Appointment.Status.KUTILMOQDA).count(),
        "qabulda": appointments_qs.filter(status=Appointment.Status.QABULDA).count(),
        "yakunlandi": appointments_qs.filter(status=Appointment.Status.YAKUNLANDI).count(),
    }


def queue_view(request):
    # Ressepshen sahifasi: to'liq navbatni ko'rsatadi, sana filtri o'chirilgan.
    bugungilar = Appointment.objects.all().select_related("doctor")

    tanlangan_shifokor = request.GET.get("doctor", "")
    tanlangan_holat = request.GET.get("status", "")
    qidiruv = request.GET.get("q", "").strip()

    appointments = bugungilar
    if tanlangan_shifokor:
        appointments = appointments.filter(doctor_id=tanlangan_shifokor)
    if tanlangan_holat:
        appointments = appointments.filter(status=tanlangan_holat)
    if qidiruv:
        appointments = appointments.filter(
            Q(patient_name__icontains=qidiruv) | Q(phone_number__icontains=qidiruv)
        )

    appointments = appointments.order_by("appointment_time", "created_at")

    context = {
        "appointments": appointments,
        "doctors": Doctor.objects.all(),
        "statistika": bugungi_statistika(bugungilar),
        "tanlangan_shifokor": tanlangan_shifokor,
        "tanlangan_holat": tanlangan_holat,
        "qidiruv": qidiruv,
    }
    return render(request, "clinic/queue.html", context)


def advance_status_view(request, pk):
    # Ressepshendagi tugma bosilganda navbat holatini keyingi bosqichga o'tkazadi
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, pk=pk)
        appointment.keyingi_statusga_otish()
        appointment.save()

    return redirect("queue")


def cancel_appointment_view(request, pk):
    # Ressepshen bemor kelmasa yoki xato kiritilsa, yozuvni butunlay o'chira oladi
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, pk=pk)
        appointment.delete()
        messages.info(request, "Yozuv bekor qilindi.")

    return redirect("queue")


def doctor_login_view(request):
    # Shifokor login/parol bilan shaxsiy kabinetiga kiradi
    if request.user.is_authenticated:
        return redirect("doctor_cabinet")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("doctor_cabinet")
    else:
        form = AuthenticationForm()

    return render(request, "clinic/login.html", {"form": form})


def doctor_logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("home")


@login_required
def doctor_cabinet_view(request):
    # Faqat tizimga kirgan shifokor o'zining bemorlar jadvalini ko'radi.
    doctor = getattr(request.user, "doctor_profile", None)

    if doctor is None:
        messages.error(
            request,
            "Sizning hisobingiz hech qanday shifokor profiliga bog'lanmagan. Administratorga murojaat qiling.",
        )
        return render(request, "clinic/doctor_cabinet.html", {"doctor": None})

    qidiruv = request.GET.get("q", "").strip()
    tanlangan_holat = request.GET.get("status", "")
    appointments = doctor.appointments.all()

    if tanlangan_holat:
        appointments = appointments.filter(status=tanlangan_holat)
    if qidiruv:
        appointments = appointments.filter(
            Q(patient_name__icontains=qidiruv) | Q(phone_number__icontains=qidiruv)
        )

    appointments = appointments.order_by("appointment_time", "created_at")

    context = {
        "doctor": doctor,
        "appointments": appointments,
        "statistika": bugungi_statistika(appointments),
        "qidiruv": qidiruv,
        "tanlangan_holat": tanlangan_holat,
    }
    return render(request, "clinic/doctor_cabinet.html", context)


@login_required
def doctor_advance_status_view(request, pk):
    # Shifokor faqat O'ZINING bemori holatini o'zgartira oladi: doctor__user=request.user
    # boshqa shifokorning yozuviga urinib ko'rsa, 404 qaytadi
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, pk=pk, doctor__user=request.user)
        appointment.keyingi_statusga_otish()
        appointment.save()

    return redirect("doctor_cabinet")


@login_required
def doctor_cancel_appointment_view(request, pk):
    # Shifokor faqat o'zining bemorini o'chira oladi
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, pk=pk, doctor__user=request.user)
        appointment.delete()
        messages.info(request, "Bemor yozuvi o'chirildi.")

    return redirect("doctor_cabinet")
