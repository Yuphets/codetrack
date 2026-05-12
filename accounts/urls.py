from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("register/", views.register, name="register"),
    path("login/", views.CodeTrackLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/", views.profile, name="profile"),
    path("sections/", views.section_manage, name="section_manage"),
    path("sections/new/", views.section_edit, name="section_create"),
    path("sections/<int:pk>/", views.section_edit, name="section_edit"),
    path("admin/users/", views.user_manage, name="user_manage"),
    path("admin/users/<int:pk>/", views.user_role_edit, name="user_role_edit"),
    path("leaderboard/", views.leaderboard_view, name="leaderboard"),
    path("api/dashboard/", views.dashboard_api, name="dashboard_api"),
]
