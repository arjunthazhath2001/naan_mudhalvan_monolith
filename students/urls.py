# students/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('students/register/<int:job_fair_id>/', views.register_for_job_fair, name='register_for_job_fair'),
    path('students/registration-success/', views.registration_success, name='student_registration_success'),
    path('students/login/', views.student_login, name='student_login'),
    path('students/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('students/logout/', views.student_logout, name='student_logout'),
    path('students/mark-attendance/<int:job_fair_id>/<int:recruiter_id>/', views.mark_recruiter_attendance, name='mark_attendance'),
]