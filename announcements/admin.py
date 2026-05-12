from django.contrib import admin
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "audience", "is_published", "publish_at", "created_by")
    list_filter = ("audience", "is_published")
    search_fields = ("title", "body")
