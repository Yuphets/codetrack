from datetime import timedelta
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from accounts.decorators import instructor_required
from problems.models import Problem, Submission


@instructor_required
def analytics_dashboard(request):
    since = timezone.now() - timedelta(days=30)
    trend = (
        Submission.objects.filter(submitted_at__gte=since)
        .extra(select={"day": "date(submitted_at)"})
        .values("day")
        .annotate(total=Count("id"), accepted=Count("id", filter=Q(status=Submission.Status.ACCEPTED)))
        .order_by("day")
    )
    topics = (
        Problem.objects.values("topic")
        .annotate(attempts=Count("submissions"), accepted=Count("submissions", filter=Q(submissions__status=Submission.Status.ACCEPTED)))
        .order_by("topic")
    )
    students = User.objects.filter(profile__role="student").annotate(
        solved=Count("submissions__problem", filter=Q(submissions__status=Submission.Status.ACCEPTED), distinct=True),
        attempts=Count("submissions"),
    )
    return render(request, "progress/analytics.html", {"trend": list(trend), "topics": list(topics), "students": students})


@instructor_required
def analytics_api(request):
    topics = list(
        Problem.objects.values("topic")
        .annotate(attempts=Count("submissions"), accepted=Count("submissions", filter=Q(submissions__status=Submission.Status.ACCEPTED)))
        .order_by("topic")
    )
    trend = list(
        Submission.objects.extra(select={"day": "date(submitted_at)"})
        .values("day")
        .annotate(total=Count("id"), accepted=Count("id", filter=Q(status=Submission.Status.ACCEPTED)))
        .order_by("day")[:30]
    )
    return JsonResponse({"topics": topics, "trend": trend})
