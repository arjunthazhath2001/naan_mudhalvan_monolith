from django.urls import path
from . import views

urlpatterns = [
    path("pteam/login", views.login_view, name="login"),
    path("pteam/index", views.index, name="index"),  # Job Fairs - default home
    path("pteam/companies", views.companies, name="companies"),  # Companies page
    path("pteam/get-recruiters/<int:job_fair_id>/", views.get_recruiters_for_job_fair, name="get_recruiters"),
]
