from django.urls import path
from . import views

urlpatterns = [
    path("", views.analytics_dashboard, name="analytics_dashboard"),
    path("api/", views.analytics_api, name="analytics_api"),
]
