from django.urls import path
from . import views

urlpatterns = [
    path('recruiters/login/', views.recruiter_login, name='recruiter_login'),
    path('recruiters/dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('recruiters/logout/', views.recruiter_logout, name='recruiter_logout'),
    # New API endpoints for status updates
    path('recruiters/update-student-status/', views.update_student_status, name='update_student_status'),
    path('recruiters/update-round-status/', views.update_round_status, name='update_round_status'),
    path('recruiters/update-student-notes/', views.update_student_notes, name='update_student_notes'),
]