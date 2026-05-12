from django.urls import path
from . import views

urlpatterns = [
    path("", views.problem_list, name="problem_list"),
    path("manage/", views.problem_manage, name="problem_manage"),
    path("manage/new/", views.problem_edit, name="problem_create"),
    path("manage/<int:pk>/", views.problem_edit, name="problem_edit"),
    path("<slug:slug>/", views.problem_detail, name="problem_detail"),
    path("<slug:slug>/api/submit/", views.submit_api, name="submit_api"),
]
