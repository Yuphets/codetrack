from django.contrib import admin
from .models import Profile, Section


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "student_id", "section_ref", "section", "updated_at")
    list_filter = ("role", "section_ref", "section")
    search_fields = ("user__username", "user__first_name", "user__last_name", "student_id", "section")


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "instructor", "is_active", "created_at")
    list_filter = ("is_active", "instructor")
    search_fields = ("name", "code", "instructor__username", "instructor__first_name", "instructor__last_name")
    prepopulated_fields = {"code": ("name",)}
