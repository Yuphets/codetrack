from django.contrib import admin
from .models import Answer, Question, Quiz, QuizAttempt, QuizRetakePermission


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "topic", "is_active", "created_at")
    list_filter = ("topic", "is_active")
    search_fields = ("title", "description")
    inlines = [QuestionInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "quiz", "score", "total", "submitted_at")
    list_filter = ("quiz",)


admin.site.register(Answer)
admin.site.register(QuizRetakePermission)
