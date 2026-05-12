from django import forms
from .models import Question, Quiz


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ("title", "description", "topic", "is_active")


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ("quiz", "prompt", "choice_a", "choice_b", "choice_c", "choice_d", "correct_choice", "explanation")
