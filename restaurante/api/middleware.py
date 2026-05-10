import uuid


class RequestIDMiddleware:
    """Attach a stable request identifier for logs, clients, and support."""

    header_name = 'HTTP_X_REQUEST_ID'
    response_header = 'X-Request-ID'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.META.get(self.header_name) or uuid.uuid4().hex
        request.request_id = request_id

        response = self.get_response(request)
        response[self.response_header] = request_id
        return response
