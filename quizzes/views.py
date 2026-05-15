from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from accounts.decorators import instructor_required
from .forms import QuestionForm, QuizForm
from .models import Answer, Question, Quiz, QuizAttempt, QuizRetakePermission


@login_required
def quiz_list(request):
    quizzes = Quiz.objects.filter(is_active=True).prefetch_related("questions")
    attempted_quiz_ids = set(request.user.quiz_attempts.values_list("quiz_id", flat=True))
    retake_quiz_ids = set(
        QuizRetakePermission.objects.filter(student=request.user, used_at__isnull=True).values_list("quiz_id", flat=True)
    )
    return render(
        request,
        "quizzes/quiz_list.html",
        {"quizzes": quizzes, "attempted_quiz_ids": attempted_quiz_ids, "retake_quiz_ids": retake_quiz_ids},
    )


@login_required
def quiz_take(request, pk):
    quiz = get_object_or_404(Quiz.objects.prefetch_related("questions"), pk=pk, is_active=True)
    questions = list(quiz.questions.all())
    existing_attempt = QuizAttempt.objects.filter(student=request.user, quiz=quiz).order_by("-submitted_at").first()
    retake_permission = QuizRetakePermission.objects.filter(student=request.user, quiz=quiz, used_at__isnull=True).order_by("-created_at").first()
    if existing_attempt and not retake_permission:
        messages.info(request, "You have already taken this quiz. Ask your instructor to reopen it if you need another attempt.")
        return redirect("quiz_result", pk=existing_attempt.pk)
    if request.method == "POST":
        if existing_attempt and not retake_permission:
            return redirect("quiz_result", pk=existing_attempt.pk)
        if not questions:
            messages.error(request, "This quiz has no questions yet.")
            return redirect("quiz_list")
        score = 0
        attempt = QuizAttempt.objects.create(student=request.user, quiz=quiz, total=len(questions))
        for question in questions:
            selected = request.POST.get(f"question_{question.id}", "")
            is_correct = selected == question.correct_choice
            if is_correct:
                score += 1
            if selected:
                Answer.objects.create(attempt=attempt, question=question, selected_choice=selected, is_correct=is_correct)
        attempt.score = score
        attempt.save()
        if retake_permission:
            retake_permission.used_at = timezone.now()
            retake_permission.save(update_fields=["used_at"])
        messages.success(request, f"Quiz submitted. Score: {score}/{len(questions)}")
        return redirect("quiz_result", pk=attempt.pk)
    return render(request, "quizzes/quiz_take.html", {"quiz": quiz, "questions": questions, "is_retake": bool(retake_permission)})


@login_required
def quiz_result(request, pk):
    attempt = get_object_or_404(QuizAttempt.objects.select_related("quiz", "student").prefetch_related("answers__question"), pk=pk)
    if attempt.student != request.user and not request.user.profile.is_instructor_like:
        messages.error(request, "You cannot view that quiz result.")
        return redirect("quiz_list")
    return render(request, "quizzes/quiz_result.html", {"attempt": attempt})


@instructor_required
def quiz_manage(request):
    quizzes = Quiz.objects.select_related("created_by").prefetch_related("questions")
    if not request.user.profile.is_admin_like:
        quizzes = quizzes.filter(created_by=request.user)
    questions = Question.objects.select_related("quiz")
    if not request.user.profile.is_admin_like:
        questions = questions.filter(quiz__created_by=request.user)
    attempts = QuizAttempt.objects.select_related("student", "quiz").order_by("-submitted_at")
    if not request.user.profile.is_admin_like:
        attempts = attempts.filter(quiz__created_by=request.user)
    return render(request, "quizzes/quiz_manage.html", {"quizzes": quizzes, "questions": questions, "attempts": attempts[:30]})


@instructor_required
def quiz_reopen(request, attempt_pk):
    attempt_queryset = QuizAttempt.objects.select_related("quiz", "student")
    if not request.user.profile.is_admin_like:
        attempt_queryset = attempt_queryset.filter(quiz__created_by=request.user)
    attempt = get_object_or_404(attempt_queryset, pk=attempt_pk)
    if request.method == "POST":
        QuizRetakePermission.objects.create(
            quiz=attempt.quiz,
            student=attempt.student,
            granted_by=request.user,
            reason=request.POST.get("reason", "Instructor reopened quiz."),
        )
        messages.success(request, f"{attempt.quiz.title} was reopened for {attempt.student.get_full_name() or attempt.student.username}.")
    return redirect("quiz_manage")


@instructor_required
def quiz_edit(request, pk=None):
    if pk:
        queryset = Quiz.objects.all() if request.user.profile.is_admin_like else Quiz.objects.filter(created_by=request.user)
        quiz = get_object_or_404(queryset, pk=pk)
    else:
        quiz = None
    if request.method == "POST":
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            item = form.save(commit=False)
            if not item.created_by_id:
                item.created_by = request.user
            item.save()
            messages.success(request, "Quiz saved.")
            return redirect("quiz_manage")
    else:
        form = QuizForm(instance=quiz)
    return render(request, "quizzes/quiz_form.html", {"form": form, "quiz": quiz})


@instructor_required
def question_edit(request, pk=None):
    if pk:
        queryset = Question.objects.select_related("quiz")
        if not request.user.profile.is_admin_like:
            queryset = queryset.filter(quiz__created_by=request.user)
        question = get_object_or_404(queryset, pk=pk)
    else:
        question = None
    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Question saved.")
            return redirect("quiz_manage")
    else:
        form = QuestionForm(instance=question, user=request.user)
    return render(request, "quizzes/question_form.html", {"form": form, "question": question})


@login_required
def quiz_submit_api(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST is required."}, status=405)
    quiz = get_object_or_404(Quiz.objects.prefetch_related("questions"), pk=pk, is_active=True)
    questions = list(quiz.questions.all())
    existing_attempt = QuizAttempt.objects.filter(student=request.user, quiz=quiz).order_by("-submitted_at").first()
    retake_permission = QuizRetakePermission.objects.filter(student=request.user, quiz=quiz, used_at__isnull=True).order_by("-created_at").first()
    if existing_attempt and not retake_permission:
        return JsonResponse({"error": "Quiz already taken. Ask your instructor to reopen it."}, status=409)
    attempt = QuizAttempt.objects.create(student=request.user, quiz=quiz, total=len(questions))
    score = 0
    for question in questions:
        selected = request.POST.get(str(question.id), "")
        correct = selected == question.correct_choice
        score += 1 if correct else 0
        if selected:
            Answer.objects.create(attempt=attempt, question=question, selected_choice=selected, is_correct=correct)
    attempt.score = score
    attempt.save()
    if retake_permission:
        retake_permission.used_at = timezone.now()
        retake_permission.save(update_fields=["used_at"])
    return JsonResponse({"attempt_id": attempt.id, "score": score, "total": len(questions), "percentage": attempt.percentage})
