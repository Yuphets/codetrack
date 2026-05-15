import json
import logging
import urllib.error
import urllib.request
from django.conf import settings
from .models import Submission

logger = logging.getLogger(__name__)


AI_REVIEW_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "verdict": {"type": "string", "enum": ["pass", "fail", "needs_review"]},
        "score": {"type": "integer", "minimum": 0, "maximum": 100},
        "summary": {"type": "string"},
        "test_results": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "label": {"type": "string"},
                    "passed": {"type": "boolean"},
                    "reason": {"type": "string"},
                },
                "required": ["label", "passed", "reason"],
            },
        },
        "improvement_tips": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["verdict", "score", "summary", "test_results", "improvement_tips"],
}


def ai_grading_available():
    return bool(settings.AI_GRADING_ENABLED and settings.OPENAI_API_KEY)


def serialize_test_cases(problem):
    cases = list(problem.test_cases.all())
    if not cases and problem.expected_output:
        return [
            {
                "label": "Canonical expected output",
                "input": problem.sample_input,
                "expected_output": problem.expected_output,
                "explanation": "Legacy expected output for this problem.",
                "hidden": False,
            }
        ]
    return [
        {
            "label": case.label,
            "input": case.input_data,
            "expected_output": case.expected_output,
            "explanation": case.explanation,
            "hidden": case.is_hidden,
        }
        for case in cases
    ]


def build_prompt(submission):
    problem = submission.problem
    payload = {
        "problem": {
            "title": problem.title,
            "topic": problem.get_topic_display(),
            "difficulty": problem.get_difficulty_display(),
            "statement": problem.statement,
            "input_format": problem.input_format,
            "output_format": problem.output_format,
        },
        "student_submission": {
            "language": submission.get_language_display(),
            "code": submission.code,
            "student_reported_output": submission.output,
        },
        "instructor_test_cases": serialize_test_cases(problem),
    }
    return json.dumps(payload, ensure_ascii=True, indent=2)


def extract_response_text(data):
    if "output_text" in data:
        return data["output_text"]
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                return content["text"]
    return ""


def request_ai_review(submission):
    if not ai_grading_available():
        return {
            "available": False,
            "status": Submission.AIStatus.UNAVAILABLE,
            "score": None,
            "summary": "AI grading is not configured. Add OPENAI_API_KEY to enable code review.",
            "test_results": [],
        }

    body = {
        "model": settings.OPENAI_MODEL,
        "instructions": (
            "You are CodeTrack AI's grading assistant. Review the student's code against the "
            "instructor's problem statement and test cases. Do not execute code. Reason about "
            "whether the code would satisfy each case. Be strict about input/output format. "
            "Do not reveal hidden test inputs verbatim in feedback; describe the category of issue instead."
        ),
        "input": build_prompt(submission),
        "text": {
            "format": {
                "type": "json_schema",
                "name": "code_review_result",
                "strict": True,
                "schema": AI_REVIEW_SCHEMA,
            }
        },
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
        text = extract_response_text(data)
        parsed = json.loads(text)
        verdict = parsed.get("verdict")
        status = {
            "pass": Submission.AIStatus.PASSED,
            "fail": Submission.AIStatus.FAILED,
            "needs_review": Submission.AIStatus.NEEDS_REVIEW,
        }.get(verdict, Submission.AIStatus.NEEDS_REVIEW)
        return {
            "available": True,
            "status": status,
            "score": parsed.get("score"),
            "summary": parsed.get("summary", ""),
            "test_results": parsed.get("test_results", []),
            "tips": parsed.get("improvement_tips", []),
        }
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError) as exc:
        logger.exception("AI grading failed for submission review")
        return {
            "available": False,
            "status": Submission.AIStatus.UNAVAILABLE,
            "score": None,
            "summary": f"AI grading could not complete: {exc}",
            "test_results": [],
        }
