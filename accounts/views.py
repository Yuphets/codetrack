from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import DatabaseError, OperationalError, ProgrammingError
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from announcements.models import Announcement
from problems.models import Problem, Submission
from quizzes.models import QuizAttempt
from .decorators import admin_required, instructor_required
from .forms import ProfileForm, RegistrationForm, SectionForm, UserRoleForm
from .models import Profile, Section
from .services import leaderboard, student_metrics


DATABASE_SETUP_MESSAGE = (
    "CodeTrack AI can open the site, but the database is not ready for account changes yet. "
    "Please run migrations against the production database, then try again."
)


def landing(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "accounts/landing.html")


class CodeTrackLoginView(auth_views.LoginView):
    template_name = "registration/login.html"

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except (DatabaseError, OperationalError, ProgrammingError):
            messages.error(request, DATABASE_SETUP_MESSAGE)
            return render(request, self.template_name, {"form": self.get_form()}, status=503)


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        try:
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(request, "Welcome to CodeTrack AI. Your student account is ready.")
                return redirect("dashboard")
        except (DatabaseError, OperationalError, ProgrammingError):
            messages.error(request, DATABASE_SETUP_MESSAGE)
            return render(request, "registration/register.html", {"form": form}, status=503)
    else:
        form = RegistrationForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    profile = request.user.profile
    if profile.is_instructor_like:
        return instructor_dashboard(request)
    metrics = student_metrics(request.user)
    recent_submissions = request.user.submissions.select_related("problem")[:6]
    announcements = Announcement.objects.filter(
        is_published=True, audience__in=["all", "students"]
    ).order_by("-publish_at")[:5]
    achievements = request.user.earned_achievements.select_related("achievement")[:8]
    problems_by_topic = Problem.objects.filter(is_active=True).values("topic").annotate(total=Count("id"))
    return render(
        request,
        "accounts/dashboard.html",
        {
            "metrics": metrics,
            "recent_submissions": recent_submissions,
            "announcements": announcements,
            "achievements": achievements,
            "problems_by_topic": problems_by_topic,
            "leaders": leaderboard(5),
        },
    )


@instructor_required
def instructor_dashboard(request):
    student_count = User.objects.filter(profile__role="student").count()
    problem_count = Problem.objects.count()
    submission_count = Submission.objects.count()
    accepted_count = Submission.objects.filter(status=Submission.Status.ACCEPTED).count()
    accuracy = round((accepted_count / submission_count) * 100, 1) if submission_count else 0
    difficult_topics = (
        Problem.objects.values("topic")
        .annotate(
            attempts=Count("submissions"),
            accepted=Count("submissions", filter=Q(submissions__status=Submission.Status.ACCEPTED)),
        )
        .order_by("-attempts")
    )
    quiz_average = QuizAttempt.objects.aggregate(avg=Avg("score"))["avg"] or 0
    return render(
        request,
        "accounts/instructor_dashboard.html",
        {
            "student_count": student_count,
            "problem_count": problem_count,
            "submission_count": submission_count,
            "accuracy": accuracy,
            "difficult_topics": list(difficult_topics),
            "quiz_average": round(quiz_average, 1),
            "leaders": leaderboard(10),
        },
    )


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("profile")
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, "accounts/profile.html", {"form": form})


@instructor_required
def section_manage(request):
    profile = request.user.profile
    sections = Section.objects.select_related("instructor").prefetch_related("students__user")
    if not profile.is_admin_like:
        sections = sections.filter(instructor=request.user)
    return render(request, "accounts/section_manage.html", {"sections": sections})


@instructor_required
def section_edit(request, pk=None):
    profile = request.user.profile
    if pk:
        queryset = Section.objects.all() if profile.is_admin_like else Section.objects.filter(instructor=request.user)
        section = get_object_or_404(queryset, pk=pk)
    else:
        section = None
    if request.method == "POST":
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            item = form.save(commit=False)
            if not item.instructor_id:
                item.instructor = request.user
            item.save()
            messages.success(request, "Section saved.")
            return redirect("section_manage")
    else:
        form = SectionForm(instance=section)
    return render(request, "accounts/section_form.html", {"form": form, "section": section})


@admin_required
def user_manage(request):
    users = User.objects.select_related("profile", "profile__section_ref").order_by("profile__role", "last_name", "username")
    return render(request, "accounts/user_manage.html", {"users": users})


@admin_required
def user_role_edit(request, pk):
    target = get_object_or_404(User.objects.select_related("profile"), pk=pk)
    if request.method == "POST":
        form = UserRoleForm(request.POST, instance=target)
        if form.is_valid():
            form.save()
            messages.success(request, f"{target.username} was updated.")
            return redirect("user_manage")
    else:
        form = UserRoleForm(instance=target)
    return render(request, "accounts/user_role_form.html", {"form": form, "target": target})


@login_required
def leaderboard_view(request):
    return render(request, "accounts/leaderboard.html", {"leaders": leaderboard(50)})


@login_required
def dashboard_api(request):
    if request.user.profile.is_instructor_like:
        data = {
            "students": User.objects.filter(profile__role="student").count(),
            "problems": Problem.objects.count(),
            "submissions": Submission.objects.count(),
        }
    else:
        data = student_metrics(request.user)
    return JsonResponse(data)
