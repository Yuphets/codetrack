import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from accounts.decorators import instructor_required
from accounts.services import award_achievements, grade_submission
from .forms import ProblemForm, SubmissionForm
from .models import Problem, Submission

logger = logging.getLogger(__name__)


@login_required
def problem_list(request):
    problems = Problem.objects.filter(is_active=True)
    topic = request.GET.get("topic")
    difficulty = request.GET.get("difficulty")
    if topic:
        problems = problems.filter(topic=topic)
    if difficulty:
        problems = problems.filter(difficulty=difficulty)
    solved_ids = set(
        Submission.objects.filter(student=request.user, status=Submission.Status.ACCEPTED).values_list("problem_id", flat=True)
    )
    return render(
        request,
        "problems/problem_list.html",
        {"problems": problems, "solved_ids": solved_ids, "topics": Problem.Topic.choices, "difficulties": Problem.Difficulty.choices},
    )


@login_required
def problem_detail(request, slug):
    problem = get_object_or_404(Problem, slug=slug, is_active=True)
    if request.method == "POST":
        form = SubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = request.user
            submission.problem = problem
            submission.status, submission.score, submission.feedback = grade_submission(problem, submission.output)
            try:
                submission.save()
                if submission.status == Submission.Status.ACCEPTED:
                    award_achievements(request.user)
                    messages.success(request, submission.feedback)
                else:
                    messages.warning(request, submission.feedback)
                return redirect("problem_detail", slug=problem.slug)
            except IntegrityError:
                messages.info(request, "You already solved this problem. New accepted duplicates are not recorded.")
                return redirect("problem_detail", slug=problem.slug)
            except Exception:
                logger.exception("Submission failed for problem %s", problem.slug)
                messages.error(request, "We could not save your submission. Please try again.")
    else:
        form = SubmissionForm(initial={"language": "python"})
    submissions = Submission.objects.filter(student=request.user, problem=problem)[:10]
    return render(request, "problems/problem_detail.html", {"problem": problem, "form": form, "submissions": submissions})


@instructor_required
def problem_manage(request):
    problems = Problem.objects.all().order_by("topic", "title")
    return render(request, "problems/problem_manage.html", {"problems": problems})


@instructor_required
def problem_edit(request, pk=None):
    problem = get_object_or_404(Problem, pk=pk) if pk else None
    if request.method == "POST":
        form = ProblemForm(request.POST, instance=problem)
        if form.is_valid():
            item = form.save(commit=False)
            if not item.created_by_id:
                item.created_by = request.user
            item.save()
            messages.success(request, "Problem saved.")
            return redirect("problem_manage")
    else:
        form = ProblemForm(instance=problem)
    return render(request, "problems/problem_form.html", {"form": form, "problem": problem})


@login_required
def submit_api(request, slug):
    if request.method != "POST":
        return JsonResponse({"error": "POST is required."}, status=405)
    problem = get_object_or_404(Problem, slug=slug, is_active=True)
    language = request.POST.get("language")
    code = request.POST.get("code", "")
    output = request.POST.get("output", "")
    if language not in dict(Submission.Language.choices):
        return JsonResponse({"error": "Unsupported language."}, status=400)
    if not code.strip():
        return JsonResponse({"error": "Code is required."}, status=400)
    status, score, feedback = grade_submission(problem, output)
    try:
        submission = Submission.objects.create(
            student=request.user,
            problem=problem,
            language=language,
            code=code,
            output=output,
            status=status,
            score=score,
            feedback=feedback,
        )
    except IntegrityError:
        return JsonResponse({"error": "This accepted solution is already recorded."}, status=409)
    if status == Submission.Status.ACCEPTED:
        award_achievements(request.user)
    return JsonResponse({"id": submission.id, "status": status, "score": score, "feedback": feedback})
