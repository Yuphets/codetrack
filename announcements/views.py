from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from accounts.decorators import instructor_required
from .forms import AnnouncementForm
from .models import Announcement


@login_required
def announcement_list(request):
    role = request.user.profile.role
    audience = ["all", "students"] if role == "student" else ["all", "instructors"]
    announcements = Announcement.objects.filter(is_published=True, audience__in=audience)
    return render(request, "announcements/announcement_list.html", {"announcements": announcements})


@instructor_required
def announcement_manage(request):
    announcements = Announcement.objects.all()
    return render(request, "announcements/announcement_manage.html", {"announcements": announcements})


@instructor_required
def announcement_edit(request, pk=None):
    announcement = get_object_or_404(Announcement, pk=pk) if pk else None
    if request.method == "POST":
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            item = form.save(commit=False)
            if not item.created_by_id:
                item.created_by = request.user
            item.save()
            messages.success(request, "Announcement saved.")
            return redirect("announcement_manage")
    else:
        form = AnnouncementForm(instance=announcement)
    return render(request, "announcements/announcement_form.html", {"form": form, "announcement": announcement})
