from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    student_id = forms.CharField(max_length=40, required=False)
    section = forms.CharField(max_length=80, required=False)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "student_id", "section", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            profile = user.profile
            profile.role = Profile.Role.STUDENT
            profile.student_id = self.cleaned_data.get("student_id", "")
            profile.section = self.cleaned_data.get("section", "")
            profile.save()
        return user


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()

    class Meta:
        model = Profile
        fields = ("student_id", "section", "bio")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].initial = self.instance.user.first_name
        self.fields["last_name"].initial = self.instance.user.last_name
        self.fields["email"].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.user.first_name = self.cleaned_data["first_name"]
        profile.user.last_name = self.cleaned_data["last_name"]
        profile.user.email = self.cleaned_data["email"]
        if commit:
            profile.user.save()
            profile.save()
        return profile
