from django.db import connections
from django.db.utils import OperationalError
from django.http import JsonResponse


def healthz(request):
    database = "ok"
    status = 200
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except OperationalError:
        database = "unavailable"
        status = 503
    return JsonResponse({"status": "ok" if status == 200 else "degraded", "database": database}, status=status)
