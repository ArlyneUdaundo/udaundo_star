from django.db import models
from django.urls import reverse
class Specialty(models.Model):
    name=models.CharField(max_length=80); slug=models.SlugField(unique=True)
    def __str__(self): return self.name
class Doctor(models.Model):
    full_name=models.CharField(max_length=120); specialty=models.ForeignKey(Specialty,on_delete=models.PROTECT,related_name='doctors')
    bio=models.TextField(); consultation_fee=models.DecimalField(max_digits=8,decimal_places=2); photo=models.ImageField(upload_to='doctors/',blank=True)
    is_accepting=models.BooleanField(default=True); date_created=models.DateTimeField(auto_now_add=True)
    def get_absolute_url(self): return reverse('doctor_detail',args=[self.pk])
    def __str__(self): return self.full_name
class Appointment(models.Model):
    VISITS=[('In-Clinic','In-Clinic'),('Teleconsultation','Teleconsultation')]; STATUS=[('Pending','Pending'),('Confirmed','Confirmed'),('Cancelled','Cancelled')]; SLOTS=[(x,x) for x in ['09:00','10:00','11:00','13:00','14:00','15:00']]
    doctor=models.ForeignKey(Doctor,on_delete=models.CASCADE,related_name='appointments'); patient_name=models.CharField(max_length=120); email=models.EmailField(blank=True); phone=models.CharField(max_length=20); appointment_date=models.DateField(); time_slot=models.CharField(max_length=5,choices=SLOTS); visit_type=models.CharField(max_length=20,choices=VISITS); reason=models.TextField(max_length=300); status=models.CharField(max_length=10,choices=STATUS,default='Pending'); date_created=models.DateTimeField(auto_now_add=True); reference=models.CharField(max_length=16,unique=True,editable=False)
    def save(self,*args,**kwargs):
        creating=not self.pk; super().save(*args,**kwargs)
        if creating and not self.reference:
            self.reference=f'MB{self.doctor_id:02d}{self.pk:04d}'; super().save(update_fields=['reference'])
    def __str__(self): return self.reference
