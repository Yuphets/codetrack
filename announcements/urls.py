from django.urls import path
from . import views

urlpatterns = [
    path("", views.announcement_list, name="announcement_list"),
    path("manage/", views.announcement_manage, name="announcement_manage"),
    path("manage/new/", views.announcement_edit, name="announcement_create"),
    path("manage/<int:pk>/", views.announcement_edit, name="announcement_edit"),
]
