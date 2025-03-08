from django.urls import path
from . import views


urlpatterns = [
    path('students/register/<int:job_fair_id>/', views.register_for_job_fair, name='register_for_job_fair'),
    path('students/registration-success/', views.registration_success, name='registration_success'),
    path('students/mark-attendance/<int:job_fair_id>/<int:recruiter_id>/', views.mark_recruiter_attendance, name='mark_attendance'),
]