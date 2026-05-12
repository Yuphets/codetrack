from django import forms
from .models import Problem, Submission


class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = (
            "title",
            "slug",
            "topic",
            "difficulty",
            "statement",
            "input_format",
            "output_format",
            "sample_input",
            "sample_output",
            "expected_output",
            "points",
            "is_active",
        )


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ("language", "code", "output")
        widgets = {
            "code": forms.Textarea(attrs={"id": "code-field"}),
            "output": forms.Textarea(attrs={"rows": 5}),
        }
