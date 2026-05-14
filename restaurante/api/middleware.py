import uuid

from django.conf import settings
from django.http import JsonResponse


class RequestIDMiddleware:
    """Attach a stable request identifier for logs, clients, and support."""

    header_name = 'HTTP_X_REQUEST_ID'
    response_header = 'X-Request-ID'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.META.get(self.header_name) or uuid.uuid4().hex
        request.request_id = request_id

        try:
            response = self.get_response(request)
        except Exception as exc:
            if not request.path.startswith('/api/'):
                raise
            payload = {
                'detail': 'Internal server error.',
                'code': 'server_error',
                'request_id': request_id,
            }
            if settings.DEBUG:
                payload['exception'] = exc.__class__.__name__
                payload['debug_detail'] = str(exc)
            response = JsonResponse(payload, status=500)
        response[self.response_header] = request_id
        return response
