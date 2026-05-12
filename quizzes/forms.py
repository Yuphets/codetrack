from django import forms
from .models import Question, Quiz


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ("title", "description", "topic", "is_active")


class QuestionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and not user.profile.is_admin_like:
            self.fields["quiz"].queryset = Quiz.objects.filter(created_by=user)

    class Meta:
        model = Question
        fields = ("quiz", "prompt", "choice_a", "choice_b", "choice_c", "choice_d", "correct_choice", "explanation")
