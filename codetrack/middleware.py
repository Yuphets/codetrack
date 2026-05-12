from django.conf import settings
from django.http import HttpResponse


class RequireConfiguredDatabaseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allowed_paths = ("/healthz/", "/static/", "/favicon.ico")
        if not settings.DATABASE_CONFIGURED and not request.path.startswith(allowed_paths):
            return HttpResponse(
                "CodeTrack AI is not connected to a production database. "
                "Set DATABASE_URL or POSTGRES_URL in Vercel Environment Variables, then redeploy.",
                status=503,
                content_type="text/plain",
            )
        return self.get_response(request)
