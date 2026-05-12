from django.db import models
from django.conf import settings
from django.utils import timezone


class Announcement(models.Model):
    title = models.CharField(max_length=180)
    body = models.TextField()
    audience = models.CharField(
        max_length=20,
        choices=[("all", "All"), ("students", "Students"), ("instructors", "Instructors")],
        default="all",
    )
    is_published = models.BooleanField(default=True)
    publish_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-publish_at"]
        indexes = [models.Index(fields=["audience", "is_published", "publish_at"])]

    def __str__(self):
        return self.title
