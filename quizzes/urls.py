from django.urls import path
from . import views

urlpatterns = [
    path("", views.quiz_list, name="quiz_list"),
    path("manage/", views.quiz_manage, name="quiz_manage"),
    path("manage/attempts/<int:attempt_pk>/reopen/", views.quiz_reopen, name="quiz_reopen"),
    path("manage/new/", views.quiz_edit, name="quiz_create"),
    path("manage/<int:pk>/", views.quiz_edit, name="quiz_edit"),
    path("questions/new/", views.question_edit, name="question_create"),
    path("questions/<int:pk>/", views.question_edit, name="question_edit"),
    path("<int:pk>/", views.quiz_take, name="quiz_take"),
    path("results/<int:pk>/", views.quiz_result, name="quiz_result"),
    path("<int:pk>/api/submit/", views.quiz_submit_api, name="quiz_submit_api"),
]
