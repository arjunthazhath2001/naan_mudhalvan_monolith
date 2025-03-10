from django.urls import path
from . import views

urlpatterns = [
    path('recruiters/login/', views.recruiter_login, name='recruiter_login'),
    path('recruiters/dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('recruiters/logout/', views.recruiter_logout, name='recruiter_logout'),
]