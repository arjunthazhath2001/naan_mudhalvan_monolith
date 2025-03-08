from django.urls import path
from . import views

urlpatterns = [
    path("pteam/login", views.login_view, name="login"),
    path("pteam/index", views.index, name="index"),
    path("pteam/companies", views.companies, name="companies"),
    path("pteam/get-recruiters/<int:job_fair_id>/", views.get_recruiters_for_job_fair, name="get_recruiters"),
    path("pteam/reset-password", views.reset_recruiter_password, name="reset_password"),  # Add this line
]