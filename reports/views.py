from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from accounts.decorators import instructor_required
from problems.models import Problem, Submission
from .models import ReportRequest


@instructor_required
def report_center(request):
    sections = User.objects.filter(profile__role="student").exclude(profile__section="").values_list("profile__section", flat=True).distinct()
    return render(request, "reports/report_center.html", {"sections": sections})


@instructor_required
def student_report_pdf(request):
    section = request.GET.get("section", "")
    students = User.objects.filter(profile__role="student").select_related("profile")
    if section:
        students = students.filter(profile__section=section)
    students = students.annotate(
        solved=Count("submissions__problem", filter=Q(submissions__status=Submission.Status.ACCEPTED), distinct=True),
        attempts=Count("submissions"),
    ).order_by("profile__section", "last_name", "first_name")
    topics = Problem.objects.values("topic").annotate(
        attempts=Count("submissions"),
        accepted=Count("submissions", filter=Q(submissions__status=Submission.Status.ACCEPTED)),
    )
    ReportRequest.objects.create(requested_by=request.user, section=section)
    html = render_to_string("reports/student_report_pdf.html", {"students": students, "topics": topics, "section": section or "All"})
    try:
        from weasyprint import HTML
        pdf = HTML(string=html, base_url=request.build_absolute_uri("/")).write_pdf()
    except OSError as exc:
        return HttpResponse(
            f"PDF generation is unavailable because WeasyPrint native libraries are missing: {exc}",
            status=503,
            content_type="text/plain",
        )
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="codetrack-report.pdf"'
    return response
