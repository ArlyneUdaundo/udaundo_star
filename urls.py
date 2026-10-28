from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from clinic import views
urlpatterns = [path('admin/',admin.site.urls),path('',views.doctor_list,name='doctor_list'),path('doctors/<int:pk>/',views.doctor_detail,name='doctor_detail'),path('doctors/<int:pk>/book/',views.book_appointment,name='book_appointment'),path('appointments/<int:pk>/confirmation/',views.confirmation,name='confirmation'),path('manage/doctors/',views.manage_doctors,name='manage_doctors'),path('manage/doctors/add/',views.doctor_form,name='doctor_add'),path('manage/doctors/<int:pk>/edit/',views.doctor_form,name='doctor_edit'),path('manage/doctors/<int:pk>/delete/',views.delete_doctor,name='delete_doctor'),path('manage/doctors/<int:pk>/toggle/',views.toggle_doctor,name='toggle_doctor'),path('manage/appointments/',views.manage_appointments,name='manage_appointments'),path('manage/appointments/<int:pk>/<str:action>/',views.appointment_action,name='appointment_action')]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
