from django.db import models
from django.conf import settings


class ReportRequest(models.Model):
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="report_requests")
    section = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        target = self.section or "All sections"
        return f"{target} report requested by {self.requested_by.username}"
