from django.urls import path
from . import views

urlpatterns = [
    path("recruiter/login", views.login_view, name="recruiter_login"),
    path("recruiter/index", views.index, name="recruiter_index"),
    # Add more recruiter routes as needed
]