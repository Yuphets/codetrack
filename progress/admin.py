from django.contrib import admin
from .models import ProgressSnapshot


@admin.register(ProgressSnapshot)
class ProgressSnapshotAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "solved_count", "attempted_count", "quiz_average", "accuracy")
    list_filter = ("date",)
    search_fields = ("student__username",)
