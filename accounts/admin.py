from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "student_id", "section", "updated_at")
    list_filter = ("role", "section")
    search_fields = ("user__username", "user__first_name", "user__last_name", "student_id", "section")
