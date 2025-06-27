import logging
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.http import Http404

log = logging.getLogger(__name__)


class ExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exc):
        log.exception("Unhandled exception")
        is_api = request.path.startswith("/detect/api/")

        if is_api:
            return JsonResponse({"detail": str(exc)}, status=500)

        if isinstance(exc, Http404):
            return TemplateResponse(request, "404.html", status=404)

        return TemplateResponse(request, "500.html", status=500)
