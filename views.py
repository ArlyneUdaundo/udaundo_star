from django.contrib import messages
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator
from .forms import AppointmentForm, DoctorForm
from .models import Appointment, Doctor, Specialty


def is_hx(request):
    return request.headers.get("HX-Request") == "true"


def doctor_list(request):
    qs = Doctor.objects.select_related("specialty").all()
    q = request.GET.get("q", "").strip()
    spec = request.GET.get("specialty", "")
    sort = request.GET.get("sort", "name")
    if q:
        qs = qs.filter(Q(full_name__icontains=q) | Q(bio__icontains=q))
    if spec:
        qs = qs.filter(specialty__slug=spec)
    sort_map = {"fee_low": "consultation_fee", "fee_high": "-consultation_fee", "name": "full_name"}
    qs = qs.order_by(sort_map.get(sort, "full_name"))
    page = Paginator(qs, 6).get_page(request.GET.get("page"))
    context = {
        "doctors": page,
        "specialties": Specialty.objects.all().order_by("name"),
        "q": q,
        "selected_specialty": spec,
        "sort": sort,
        "count": qs.count(),
        "page_obj": page,
    }
    template = "clinic/partials/_doctor_grid.html" if is_hx(request) else "clinic/doctor_list.html"
    return render(request, template, context)


def doctor_detail(request, pk):
    return render(request, "clinic/doctor_detail.html", {"doctor": get_object_or_404(Doctor, pk=pk)})


def book_appointment(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if not doctor.is_accepting:
        raise Http404("Doctor is not accepting patients.")

    form = AppointmentForm(request.POST or None, doctor=doctor)
    selected_date = request.GET.get("date") or request.POST.get("appointment_date")
    booked = []
    if selected_date:
        booked = list(
            Appointment.objects.filter(doctor=doctor, appointment_date=selected_date)
            .exclude(status="Cancelled")
            .values_list("time_slot", flat=True)
        )

    if is_hx(request) and request.method == "GET" and request.GET.get("date"):
        return render(request, "clinic/partials/_slot_options.html", {"form": form, "booked": booked})

    if request.method == "POST" and form.is_valid():
        appointment = form.save(commit=False)
        appointment.doctor = doctor
        appointment.save()
        if is_hx(request):
            response = HttpResponse("")
            response["HX-Redirect"] = reverse("confirmation", args=[appointment.pk])
            response["HX-Trigger"] = '{"toast": {"text": "Appointment booked successfully."}}'
            return response
        return redirect("confirmation", appointment.pk)

    template = "clinic/partials/_booking_form.html" if is_hx(request) else "clinic/appointment_form.html"
    return render(request, template, {"doctor": doctor, "form": form, "booked": booked})


def confirmation(request, pk):
    return render(request, "clinic/appointment_success.html", {"appointment": get_object_or_404(Appointment, pk=pk)})


def manage_doctors(request):
    return render(request, "clinic/doctor_manage.html", {"doctors": Doctor.objects.select_related("specialty").all()})


def doctor_form(request, pk=None):
    obj = get_object_or_404(Doctor, pk=pk) if pk else None
    form = DoctorForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Doctor saved successfully.")
        return redirect("manage_doctors")
    return render(request, "clinic/doctor_form.html", {"form": form, "doctor": obj})


def delete_doctor(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    doctor.delete()
    return HttpResponse("")


def toggle_doctor(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    doctor.is_accepting = not doctor.is_accepting
    doctor.save(update_fields=["is_accepting"])
    return render(request, "clinic/partials/_doctor_row.html", {"doctor": doctor})


def manage_appointments(request):
    appointments = Appointment.objects.select_related("doctor").all().order_by("-date_created")
    return render(request, "clinic/appointment_manage.html", {"appointments": appointments})


def appointment_action(request, pk, action):
    appointment = get_object_or_404(Appointment, pk=pk)
    if action == "confirm":
        appointment.status = "Confirmed"
    elif action == "cancel":
        appointment.status = "Cancelled"
    else:
        raise Http404("Unknown appointment action.")
    appointment.save(update_fields=["status"])
    return render(request, "clinic/partials/_appointment_row.html", {"appointment": appointment})
