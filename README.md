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
   username: instructor
   password: ChangeMe123!
   ```

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
   ALLOWED_HOSTS=your-domain.com
   CSRF_TRUSTED_ORIGINS=https://your-domain.com
   DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE
   DB_CONN_MAX_AGE=600
   DB_SSL_REQUIRE=True
   SECURE_SSL_REDIRECT=True
   ```

2. Install requirements on the server:

   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations and collect static files:

   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

4. Serve with a WSGI server such as Gunicorn:

   ```bash
   gunicorn codetrack.wsgi:application
   ```

## Notes

- Django CSRF protection, ORM parameterization, password hashing, and role checks are used throughout the app.
- Arbitrary submitted code is not executed on the server. Students paste their program output, and CodeTrack compares it with the expected output. This avoids unsafe remote-code execution in a classroom deployment.
- Instructor and admin access is controlled through `accounts.Profile.role`; superusers can access privileged screens.
