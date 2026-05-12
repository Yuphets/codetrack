from django.contrib import admin
from .models import ReportRequest


@admin.register(ReportRequest)
class ReportRequestAdmin(admin.ModelAdmin):
    list_display = ("requested_by", "section", "created_at")
    list_filter = ("section",)
