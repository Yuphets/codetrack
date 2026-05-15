from django.contrib import admin
from .models import Achievement, Problem, ProblemTestCase, StudentAchievement, Submission


class ProblemTestCaseInline(admin.TabularInline):
    model = ProblemTestCase
    extra = 1


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ("title", "topic", "difficulty", "points", "is_active", "updated_at")
    list_filter = ("topic", "difficulty", "is_active")
    search_fields = ("title", "statement")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProblemTestCaseInline]


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("student", "problem", "language", "status", "score", "ai_status", "ai_score", "submitted_at")
    list_filter = ("language", "status", "ai_status", "problem__topic")
    search_fields = ("student__username", "problem__title")
    readonly_fields = ("submitted_at",)


admin.site.register(Achievement)
admin.site.register(StudentAchievement)
