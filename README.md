# CodeTrack AI

CodeTrack AI is a Django 4.2 web application for tracking coding progress, practice submissions, quizzes, achievements, leaderboards, instructor analytics, announcements, and PDF reports.

## Features

- Student dashboard with streaks, score, accuracy, solved problems, announcements, and badges
- Coding practice problems grouped by Loops, Arrays, OOP, and Algorithms
- Browser code editor powered by Ace Editor for Python, Java, C++, and PHP
- Output-based submission grading with safe server-side persistence
- Quizzes, quiz attempts, scoring, and answer review
- Achievements and leaderboard
- Instructor problem, quiz, question, and announcement management screens
- Analytics charts for topic difficulty, class progress, and trends
- PDF progress reports with WeasyPrint
- PostgreSQL-ready configuration using `DATABASE_URL`

## From-Scratch Setup

1. Create and enter the project folder:

   ```powershell
   mkdir codetrack_ai
   cd codetrack_ai
   ```

2. Create a virtual environment:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Create a `.env` file:

   ```env
   SECRET_KEY=replace-with-a-long-random-secret
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   CSRF_TRUSTED_ORIGINS=
   DATABASE_URL=sqlite:///db.sqlite3
   TIME_ZONE=Asia/Manila
   ```

   For PostgreSQL:

   ```env
   DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE
   DB_CONN_MAX_AGE=600
   DB_SSL_REQUIRE=True
   ```

5. Apply migrations:

   ```powershell
   python manage.py migrate
   ```

6. Create an admin account:

   ```powershell
   python manage.py createsuperuser
   ```

7. Seed demo content:

   ```powershell
   python manage.py seed_demo
   ```

   Demo instructor login:

   ```text
   admin username: codetrack_admin
   admin password: AdminChangeMe123!
   username: instructor
   password: ChangeMe123!
   ```

   The app admin can open `Users` in the navigation to promote a student account to Instructor or Admin.

8. Run the development server:

   ```powershell
   python manage.py runserver
   ```

9. Open:

   ```text
   http://127.0.0.1:8000/
   ```

## Deployment

1. Set production environment variables on your hosting platform:

   ```env
   SECRET_KEY=<strong-secret>
   DEBUG=False
   ALLOWED_HOSTS=your-domain.com,codetrack-bay.vercel.app
   CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://codetrack-bay.vercel.app
   DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE
   DB_CONN_MAX_AGE=600
   DB_SSL_REQUIRE=True
   SECURE_SSL_REDIRECT=True
   ```

   On Vercel, make sure `DATABASE_URL` is the Neon pooled PostgreSQL URL, not a localhost placeholder. If you imported Neon variables through the Vercel integration, `POSTGRES_URL` also works; the app will use it if `DATABASE_URL` still points at localhost.

   Recommended Vercel values:

   ```env
   DEBUG=False
   ALLOWED_HOSTS=codetrack-bay.vercel.app
   CSRF_TRUSTED_ORIGINS=https://codetrack-bay.vercel.app
   DATABASE_URL=<your Neon pooled connection string with sslmode=require>
   DB_CONN_MAX_AGE=0
   DB_CONN_HEALTH_CHECKS=True
   OPENAI_API_KEY=<your OpenAI API key>
   OPENAI_MODEL=gpt-4.1-mini
   AI_GRADING_ENABLED=True
   ```

   The app automatically accepts Vercel-provided `VERCEL_URL`, `VERCEL_BRANCH_URL`, and `VERCEL_PROJECT_PRODUCTION_URL`, but keeping your production domain in `ALLOWED_HOSTS` is still recommended.

2. Install requirements on the server:

   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations and collect static files:

   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

   For Vercel plus Neon, run migrations against Neon from your local machine before or after deployment:

   ```powershell
   $env:DATABASE_URL="<your Neon pooled connection string>"
   python manage.py migrate
   python manage.py seed_demo
   ```

   Then verify the deployed database connection:

   ```text
   https://codetrack-bay.vercel.app/healthz/
   ```

   If Vercel says it failed to read Django settings from `manage.py`, verify that this code change is deployed and that `.env` / `db.sqlite3` are not tracked in git. If `/healthz/` returns `misconfigured`, Vercel is missing `DATABASE_URL` or `POSTGRES_URL`.

## AI Grading

Instructors can add test cases to coding problems. When a student submits code, CodeTrack first keeps the existing output comparison as a deterministic fallback, then asks the AI grader to review the code against the instructor test cases if `OPENAI_API_KEY` is configured.

Set these in Vercel to enable AI review:

```env
OPENAI_API_KEY=<your OpenAI API key>
OPENAI_MODEL=gpt-4.1-mini
AI_GRADING_ENABLED=True
```

The AI reviewer does not execute untrusted student code. It inspects the code, problem statement, and instructor test cases, then returns a structured verdict, score, per-case notes, and improvement tips.

4. Serve with a WSGI server such as Gunicorn:

   ```bash
   gunicorn codetrack.wsgi:application
   ```

## Notes

- Django CSRF protection, ORM parameterization, password hashing, and role checks are used throughout the app.
- Arbitrary submitted code is not executed on the server. Students paste their program output, and CodeTrack compares it with the expected output. This avoids unsafe remote-code execution in a classroom deployment.
- Instructor and admin access is controlled through `accounts.Profile.role`; superusers can access privileged screens.
