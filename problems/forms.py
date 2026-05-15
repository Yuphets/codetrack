from django import forms
from django.forms import inlineformset_factory
from .models import Problem, ProblemTestCase, Submission


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


ProblemTestCaseFormSet = inlineformset_factory(
    Problem,
    ProblemTestCase,
    fields=("label", "input_data", "expected_output", "explanation", "is_hidden", "order"),
    extra=2,
    can_delete=True,
    widgets={
        "input_data": forms.Textarea(attrs={"rows": 3}),
        "expected_output": forms.Textarea(attrs={"rows": 3}),
        "explanation": forms.Textarea(attrs={"rows": 2}),
    },
)
