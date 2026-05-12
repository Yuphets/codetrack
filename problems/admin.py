from django.contrib import admin
from .models import Achievement, Problem, StudentAchievement, Submission


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ("title", "topic", "difficulty", "points", "is_active", "updated_at")
    list_filter = ("topic", "difficulty", "is_active")
    search_fields = ("title", "statement")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("student", "problem", "language", "status", "score", "submitted_at")
    list_filter = ("language", "status", "problem__topic")
    search_fields = ("student__username", "problem__title")
    readonly_fields = ("submitted_at",)


admin.site.register(Achievement)
admin.site.register(StudentAchievement)
