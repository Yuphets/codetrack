from django.db import models
from django.conf import settings


class ProgressSnapshot(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="progress_snapshots")
    date = models.DateField()
    solved_count = models.PositiveIntegerField(default=0)
    attempted_count = models.PositiveIntegerField(default=0)
    quiz_average = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    accuracy = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        unique_together = ("student", "date")
        ordering = ["-date"]
        indexes = [models.Index(fields=["date"])]

    def __str__(self):
        return f"{self.student.username} progress on {self.date}"
