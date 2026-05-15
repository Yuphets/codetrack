from django.db import models
from django.conf import settings
from django.utils import timezone


class Problem(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    class Topic(models.TextChoices):
        LOOPS = "loops", "Loops"
        ARRAYS = "arrays", "Arrays"
        OOP = "oop", "OOP"
        ALGORITHMS = "algorithms", "Algorithms"

    title = models.CharField(max_length=180)
    slug = models.SlugField(unique=True)
    topic = models.CharField(max_length=30, choices=Topic.choices)
    difficulty = models.CharField(max_length=20, choices=Difficulty.choices)
    statement = models.TextField()
    input_format = models.TextField(blank=True)
    output_format = models.TextField(blank=True)
    sample_input = models.TextField(blank=True)
    sample_output = models.TextField(blank=True)
    expected_output = models.TextField(help_text="Canonical output used for auto-checking.")
    points = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["topic", "difficulty", "title"]
        indexes = [
            models.Index(fields=["topic", "difficulty"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.title


class ProblemTestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="test_cases")
    label = models.CharField(max_length=120, default="Test case")
    input_data = models.TextField(blank=True)
    expected_output = models.TextField()
    explanation = models.TextField(blank=True)
    is_hidden = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        visibility = "hidden" if self.is_hidden else "visible"
        return f"{self.problem.title} - {self.label} ({visibility})"


class Submission(models.Model):
    class Language(models.TextChoices):
        PYTHON = "python", "Python"
        JAVA = "java", "Java"
        CPP = "cpp", "C++"
        PHP = "php", "PHP"

    class Status(models.TextChoices):
        ACCEPTED = "accepted", "Accepted"
        WRONG_ANSWER = "wrong_answer", "Wrong Answer"

    class AIStatus(models.TextChoices):
        NOT_REQUESTED = "not_requested", "Not requested"
        UNAVAILABLE = "unavailable", "Unavailable"
        PASSED = "passed", "Passed"
        NEEDS_REVIEW = "needs_review", "Needs review"
        FAILED = "failed", "Failed"

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions")
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="submissions")
    language = models.CharField(max_length=20, choices=Language.choices)
    code = models.TextField()
    output = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices)
    score = models.PositiveIntegerField(default=0)
    feedback = models.TextField(blank=True)
    ai_status = models.CharField(max_length=20, choices=AIStatus.choices, default=AIStatus.NOT_REQUESTED)
    ai_score = models.PositiveIntegerField(null=True, blank=True)
    ai_feedback = models.TextField(blank=True)
    ai_test_results = models.JSONField(default=list, blank=True)
    submitted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(fields=["student", "status"]),
            models.Index(fields=["problem", "status"]),
            models.Index(fields=["submitted_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "problem"],
                condition=models.Q(status="accepted"),
                name="unique_accepted_submission_per_problem",
            )
        ]

    def __str__(self):
        return f"{self.student.username} - {self.problem.title} - {self.status}"


class Achievement(models.Model):
    code = models.SlugField(unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField()
    icon = models.CharField(max_length=60, default="award")
    threshold = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["threshold", "name"]

    def __str__(self):
        return self.name


class StudentAchievement(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="earned_achievements")
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name="earners")
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "achievement")
        ordering = ["-earned_at"]

    def __str__(self):
        return f"{self.student.username} earned {self.achievement.name}"
