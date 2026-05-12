from django.urls import path
from . import views

urlpatterns = [
    path("", views.report_center, name="report_center"),
    path("students.pdf", views.student_report_pdf, name="student_report_pdf"),
]
