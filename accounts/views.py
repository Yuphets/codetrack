from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from announcements.models import Announcement
from problems.models import Problem, Submission
from quizzes.models import QuizAttempt
from .decorators import instructor_required
from .forms import ProfileForm, RegistrationForm
from .services import leaderboard, student_metrics


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome to CodeTrack AI. Your student account is ready.")
            return redirect("dashboard")
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
