import re
from datetime import date
from django import forms
from .models import Doctor, Appointment

PHONE_RE = re.compile(r"^(09\d{9}|\+639\d{9})$")

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ["full_name", "specialty", "bio", "consultation_fee", "photo", "is_accepting"]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Dr. Maria Santos", "class": "input"}),
            "bio": forms.Textarea(attrs={"rows": 4, "placeholder": "Short professional biography", "class": "input"}),
            "consultation_fee": forms.NumberInput(attrs={"min": "0.01", "step": "0.01", "class": "input"}),
            "photo": forms.ClearableFileInput(attrs={"class": "input", "accept": "image/*"}),
            "is_accepting": forms.CheckboxInput(),
        }
        labels = {
            "full_name": "Doctor name",
            "consultation_fee": "Consultation fee",
            "is_accepting": "Accepting new patients",
        }
        help_texts = {
            "consultation_fee": "Must be greater than 0.",
            "photo": "Optional JPG/PNG doctor photo.",
        }

    def clean_consultation_fee(self):
        value = self.cleaned_data["consultation_fee"]
        if value <= 0:
            raise forms.ValidationError("Consultation fee must be greater than 0.")
        return value


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["patient_name", "email", "phone", "appointment_date", "time_slot", "visit_type", "reason"]
        widgets = {
            "patient_name": forms.TextInput(attrs={"class": "input", "placeholder": "Juan Dela Cruz"}),
            "email": forms.EmailInput(attrs={"class": "input", "placeholder": "juan@example.com"}),
            "phone": forms.TextInput(attrs={"class": "input", "placeholder": "09171234567"}),
            "appointment_date": forms.DateInput(attrs={"type": "date", "class": "input"}),
            "time_slot": forms.Select(attrs={"class": "input"}),
            "visit_type": forms.Select(attrs={"class": "input"}),
            "reason": forms.Textarea(attrs={"rows": 5, "maxlength": 300, "class": "input"}),
        }
        labels = {
            "patient_name": "Patient name",
            "appointment_date": "Appointment date",
            "time_slot": "Time slot",
            "visit_type": "Visit type",
            "reason": "Reason for visit",
        }
        help_texts = {
            "phone": "09XXXXXXXXX or +639XXXXXXXXX",
            "reason": "At least 10 characters, maximum 300.",
        }

    def __init__(self, *args, doctor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.doctor = doctor

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if not PHONE_RE.fullmatch(phone):
            raise forms.ValidationError("Use 09XXXXXXXXX or +639XXXXXXXXX.")
        return phone

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data["appointment_date"]
        if appointment_date < date.today():
            raise forms.ValidationError("Appointment date cannot be in the past.")
        if appointment_date.weekday() == 6:
            raise forms.ValidationError("The clinic is closed on Sundays.")
        return appointment_date

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        visit_type = cleaned.get("visit_type")
        reason = (cleaned.get("reason") or "").strip()
        appointment_date = cleaned.get("appointment_date")
        time_slot = cleaned.get("time_slot")

        if visit_type == "Teleconsultation" and not email:
            self.add_error("email", "Email is required for teleconsultation.")
        if reason and len(reason) < 10:
            self.add_error("reason", "Reason must have at least 10 characters.")
        if self.doctor and not self.doctor.is_accepting:
            raise forms.ValidationError("This doctor is not accepting patients.")
        if self.doctor and appointment_date and time_slot:
            conflict = Appointment.objects.filter(
                doctor=self.doctor,
                appointment_date=appointment_date,
                time_slot=time_slot,
            ).exclude(status="Cancelled").exclude(pk=self.instance.pk).exists()
            if conflict:
                raise forms.ValidationError("That doctor, date, and time slot is already booked.")
        return cleaned
