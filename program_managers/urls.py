from django.urls import path
from . import views

urlpatterns = [
    path("pmanager/login", views.login_view, name="program_manager_login"),
    path("pmanager/logout", views.logout_view, name="program_manager_logout"),
    path("pmanager/index", views.index, name="program_manager_index"),
    path("pmanager/companies", views.companies, name="program_manager_companies"),
    path("pmanager/analytics", views.analytics, name="program_manager_analytics"),
    path("pmanager/get-recruiters/<int:job_fair_id>/", views.get_recruiters_for_job_fair, name="program_manager_get_recruiters"),
    path("pmanager/get-company-students/<int:job_fair_id>/<int:recruiter_id>/", views.get_company_students, name="program_manager_get_company_students"),
    path("pmanager/reset-password", views.reset_recruiter_password, name="program_manager_reset_password"),
    path("pmanager/delete-recruiter", views.delete_recruiter_from_job_fair, name="program_manager_delete_recruiter"),
]