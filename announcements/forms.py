from django import forms
from .models import Announcement


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ("title", "body", "audience", "is_published", "publish_at")
        widgets = {"publish_at": forms.DateTimeInput(attrs={"type": "datetime-local"})}
