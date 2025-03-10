from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/recruiter/(?P<recruiter_id>\d+)/(?P<job_fair_id>\d+)/$', consumers.RecruiterConsumer.as_asgi()),
]