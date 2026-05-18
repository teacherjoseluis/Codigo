import uuid

from django.conf import settings
from django.http import JsonResponse


ERROR_CODES = {
    400: 'bad_request',
    401: 'not_authenticated',
    403: 'permission_denied',
    404: 'not_found',
    405: 'method_not_allowed',
    409: 'conflict',
    500: 'server_error',
}


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
        response = self._ensure_api_error_json(request, response, request_id)
        response[self.response_header] = request_id
        return response

    def _ensure_api_error_json(self, request, response, request_id):
        if not request.path.startswith('/api/') or response.status_code < 400:
            return response

        content_type = response.get('Content-Type', '')
        if content_type.startswith('application/json'):
            return response

        payload = {
            'detail': response.reason_phrase or 'Request failed.',
            'code': ERROR_CODES.get(response.status_code, 'api_error'),
            'request_id': request_id,
        }
        return JsonResponse(payload, status=response.status_code)
