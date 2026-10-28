from django.contrib import admin
from .models import Specialty, Doctor, Appointment
admin.site.register([Specialty,Doctor,Appointment])
