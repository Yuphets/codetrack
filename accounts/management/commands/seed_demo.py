from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from accounts.models import Section
from problems.models import Achievement, Problem
from quizzes.models import Question, Quiz


class Command(BaseCommand):
    help = "Seed CodeTrack AI with sample accounts, sections, problems, quizzes, and achievements."

    def handle(self, *args, **options):
        admin, created = User.objects.get_or_create(
            username="codetrack_admin",
            defaults={"email": "admin@example.com", "first_name": "CodeTrack", "last_name": "Admin", "is_staff": True, "is_superuser": True},
        )
        if created:
            admin.set_password("AdminChangeMe123!")
            admin.save()
        admin.is_staff = True
        admin.is_superuser = True
        admin.profile.role = "admin"
        admin.profile.save()
        admin.save()

        instructor, created = User.objects.get_or_create(
            username="instructor",
            defaults={"email": "instructor@example.com", "first_name": "CodeTrack", "last_name": "Instructor", "is_staff": True},
        )
        if created:
            instructor.set_password("ChangeMe123!")
            instructor.save()
        instructor.profile.role = "instructor"
        instructor.profile.save()

        Section.objects.get_or_create(
            instructor=instructor,
            code="bscs-1a",
            defaults={"name": "BSCS 1A", "description": "Default first-year programming section."},
        )

        achievements = [
            ("problem-solver", "Problem Solver", "Solved your first coding problem.", "award", 1),
            ("code-warrior", "Code Warrior", "Solved five coding problems.", "shield", 5),
            ("algorithm-master", "Algorithm Master", "Solved three algorithm problems.", "sparkles", 3),
        ]
        for code, name, description, icon, threshold in achievements:
            Achievement.objects.get_or_create(code=code, defaults={"name": name, "description": description, "icon": icon, "threshold": threshold})

        problems = [
            {
                "title": "Print Numbers One to N",
                "slug": "print-numbers-one-to-n",
                "topic": "loops",
                "difficulty": "easy",
                "statement": "Given N, print the numbers from 1 to N, one per line.",
                "sample_input": "5",
                "sample_output": "1\n2\n3\n4\n5",
                "expected_output": "1\n2\n3\n4\n5",
                "points": 10,
            },
            {
                "title": "Array Sum",
                "slug": "array-sum",
                "topic": "arrays",
                "difficulty": "easy",
                "statement": "Given a list of integers, print their sum.",
                "sample_input": "5\n1 2 3 4 5",
                "sample_output": "15",
                "expected_output": "15",
                "points": 10,
            },
            {
                "title": "Palindrome Check",
                "slug": "palindrome-check",
                "topic": "algorithms",
                "difficulty": "medium",
                "statement": "Print YES if the input word is a palindrome; otherwise print NO.",
                "sample_input": "level",
                "sample_output": "YES",
                "expected_output": "YES",
                "points": 20,
            },
        ]
        for data in problems:
            Problem.objects.get_or_create(slug=data["slug"], defaults={**data, "created_by": instructor})

        quiz, _ = Quiz.objects.get_or_create(title="Python Basics", defaults={"topic": "Python", "description": "Core syntax and control-flow checks.", "created_by": instructor})
        Question.objects.get_or_create(
            quiz=quiz,
            prompt="Which keyword starts a loop over a sequence in Python?",
            defaults={"choice_a": "for", "choice_b": "switch", "choice_c": "class", "choice_d": "echo", "correct_choice": "A", "explanation": "Python uses for to iterate over sequences."},
        )
        Question.objects.get_or_create(
            quiz=quiz,
            prompt="What is the result of len([1, 2, 3])?",
            defaults={"choice_a": "2", "choice_b": "3", "choice_c": "4", "choice_d": "Error", "correct_choice": "B", "explanation": "The list contains three items."},
        )
        self.stdout.write(self.style.SUCCESS("Demo data seeded. Admin login: codetrack_admin / AdminChangeMe123! Instructor login: instructor / ChangeMe123!"))
