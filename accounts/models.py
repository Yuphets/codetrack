from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Section(models.Model):
    name = models.CharField(max_length=80)
    code = models.SlugField(max_length=90)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sections")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("instructor", "code")
        ordering = ["instructor__last_name", "name"]
        indexes = [models.Index(fields=["is_active", "code"])]

    def __str__(self):
        owner = self.instructor.get_full_name() or self.instructor.username
        return f"{self.name} - {owner}"


class Profile(models.Model):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        INSTRUCTOR = "instructor", "Instructor"
        ADMIN = "admin", "Admin"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    student_id = models.CharField(max_length=40, blank=True)
    section = models.CharField(max_length=80, blank=True)
    section_ref = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name="students")
    leaderboard_alias = models.CharField(max_length=80, blank=True)
    show_real_name_on_leaderboard = models.BooleanField(default=False)
    show_quiz_percentage_on_leaderboard = models.BooleanField(default=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["role", "section"])]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

    @property
    def is_instructor_like(self):
        return self.role in {self.Role.INSTRUCTOR, self.Role.ADMIN} or self.user.is_staff

    @property
    def is_admin_like(self):
        return self.role == self.Role.ADMIN or self.user.is_superuser

    @property
    def display_section(self):
        return self.section_ref.name if self.section_ref else self.section


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)
        instance.profile.save()
