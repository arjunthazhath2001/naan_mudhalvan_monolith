from django.urls import path
from . import views

urlpatterns = [
    path('students/register/<int:job_fair_id>/', views.register_for_job_fair, name='register_for_job_fair'),
    path('students/registration-success/', views.registration_success, name='registration_success'),
   ]