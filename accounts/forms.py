from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Section


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    student_id = forms.CharField(max_length=40, required=False)
    section_ref = forms.ModelChoiceField(
        queryset=Section.objects.none(),
        label="Section",
        required=False,
        empty_label="Choose your section",
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "student_id", "section_ref", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["section_ref"].queryset = Section.objects.filter(is_active=True).select_related("instructor")

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
            profile.section_ref = self.cleaned_data.get("section_ref")
            profile.section = profile.section_ref.name if profile.section_ref else ""
            profile.save()
        return user


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()

    class Meta:
        model = Profile
        fields = ("student_id", "section_ref", "bio")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].initial = self.instance.user.first_name
        self.fields["last_name"].initial = self.instance.user.last_name
        self.fields["email"].initial = self.instance.user.email
        self.fields["section_ref"].queryset = Section.objects.filter(is_active=True).select_related("instructor")

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.user.first_name = self.cleaned_data["first_name"]
        profile.user.last_name = self.cleaned_data["last_name"]
        profile.user.email = self.cleaned_data["email"]
        if profile.section_ref:
            profile.section = profile.section_ref.name
        if commit:
            profile.user.save()
            profile.save()
        return profile


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ("name", "code", "description", "is_active")


class UserRoleForm(forms.ModelForm):
    role = forms.ChoiceField(choices=Profile.Role.choices)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "is_active", "is_staff")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].initial = self.instance.profile.role

    def save(self, commit=True):
        user = super().save(commit=False)
        user.profile.role = self.cleaned_data["role"]
        if user.profile.role == Profile.Role.STUDENT:
            user.is_staff = False
            user.is_superuser = False
        elif user.profile.role == Profile.Role.INSTRUCTOR:
            user.is_staff = True
            user.is_superuser = False
        elif user.profile.role == Profile.Role.ADMIN:
            user.is_staff = True
            user.is_superuser = True
        if commit:
            user.save()
            user.profile.save()
        return user
