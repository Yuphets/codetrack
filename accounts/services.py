from datetime import timedelta
from django.contrib.auth.models import User
from django.db.models import Count, Max, Q, Sum
from django.utils import timezone
from problems.models import Achievement, StudentAchievement, Submission


def normalized_text(value):
    return "\n".join(line.rstrip() for line in value.strip().splitlines()).strip()


def grade_submission(problem, output):
    if normalized_text(output) == normalized_text(problem.expected_output):
        return Submission.Status.ACCEPTED, problem.points, "Accepted. Output matches the expected result."
    return Submission.Status.WRONG_ANSWER, 0, "Wrong answer. Review the expected format and sample output."


def award_achievements(student):
    solved = Submission.objects.filter(student=student, status=Submission.Status.ACCEPTED).values("problem").distinct().count()
    topic_counts = (
        Submission.objects.filter(student=student, status=Submission.Status.ACCEPTED)
        .values("problem__topic")
        .annotate(total=Count("problem", distinct=True))
    )
    defaults = [
        ("problem-solver", "Problem Solver", "Solved your first coding problem.", "award", 1),
        ("code-warrior", "Code Warrior", "Solved five coding problems.", "shield", 5),
        ("algorithm-master", "Algorithm Master", "Solved three algorithm problems.", "sparkles", 3),
    ]
    for code, name, description, icon, threshold in defaults:
        Achievement.objects.get_or_create(
            code=code,
            defaults={"name": name, "description": description, "icon": icon, "threshold": threshold},
        )

    for achievement in Achievement.objects.all():
        qualifies = solved >= achievement.threshold
        if achievement.code == "algorithm-master":
            qualifies = any(row["problem__topic"] == "algorithms" and row["total"] >= achievement.threshold for row in topic_counts)
        if qualifies:
            StudentAchievement.objects.get_or_create(student=student, achievement=achievement)


def student_metrics(student):
    submissions = Submission.objects.filter(student=student)
    accepted = submissions.filter(status=Submission.Status.ACCEPTED)
    attempted = submissions.values("problem").distinct().count()
    solved = accepted.values("problem").distinct().count()
    total = submissions.count()
    accuracy = round((accepted.count() / total) * 100, 1) if total else 0
    score = accepted.values("problem").distinct().aggregate(total=Sum("score"))["total"] or 0
    days = set(accepted.values_list("submitted_at__date", flat=True))
    streak = 0
    cursor = timezone.localdate()
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    last_activity = submissions.aggregate(last=Max("submitted_at"))["last"]
    return {
        "attempted": attempted,
        "solved": solved,
        "accuracy": accuracy,
        "score": score,
        "streak": streak,
        "last_activity": last_activity,
    }


def leaderboard(limit=20):
    students = (
        User.objects.filter(profile__role="student")
        .select_related("profile", "profile__section_ref")
        .prefetch_related("quiz_attempts")
        .annotate(
            solved=Count("submissions__problem", filter=Q(submissions__status="accepted"), distinct=True),
            coding_score=Sum("submissions__score", filter=Q(submissions__status="accepted")),
        )
    )
    rows = []
    for student in students:
        attempts = list(student.quiz_attempts.all())
        quiz_score = sum(attempt.score for attempt in attempts)
        quiz_total = sum(attempt.total for attempt in attempts)
        quiz_percentage = round((quiz_score / quiz_total) * 100, 1) if quiz_total else None
        profile = student.profile
        public_name = profile.leaderboard_alias.strip()
        if not public_name:
            public_name = student.get_full_name() or student.username if profile.show_real_name_on_leaderboard else "Anonymous Student"
        rows.append(
            {
                "user": student,
                "public_name": public_name,
                "section": profile.display_section,
                "solved": student.solved or 0,
                "coding_score": student.coding_score or 0,
                "quiz_attempts": len(attempts),
                "quiz_percentage": quiz_percentage,
                "show_quiz_percentage": profile.show_quiz_percentage_on_leaderboard,
            }
        )
    rows.sort(
        key=lambda row: (
            row["quiz_percentage"] if row["quiz_percentage"] is not None else -1,
            row["coding_score"],
            row["solved"],
        ),
        reverse=True,
    )
    for index, row in enumerate(rows, start=1):
        if row["public_name"] == "Anonymous Student":
            row["public_name"] = f"Anonymous Student #{index}"
    return rows[:limit]
