# insights/urls.py
from django.urls import path
from . import views
from .views import analyze_facebook

urlpatterns = [
     path('analyze/', analyze_facebook),
     path("request-report/", views.request_report, name="request_report"),
     path("reports/", views.get_reports, name="get_reports"),
     path("reports/<str:report_id>/", views.get_report, name="get_report"),
]
