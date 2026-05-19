import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


logger = logging.getLogger(__name__)


class DomainValidationError(ValueError):
    def __init__(self, detail, errors=None):
        super().__init__(detail)
        self.detail = detail
        self.errors = errors


def _request_id(context):
    request = context.get('request') if context else None
    return getattr(request, 'request_id', None)


def _error_payload(detail, code, context, errors=None):
    payload = {
        'detail': detail,
        'code': code,
    }
    request_id = _request_id(context)
    if request_id:
        payload['request_id'] = request_id
    if errors is not None:
        payload['errors'] = errors
    return payload


def domain_exception_handler(exc, context):
    """Map domain-layer exceptions to stable API error responses."""
    response = exception_handler(exc, context)
    if response is not None:
        if response.status_code >= 400:
            response.data = _normalize_drf_error(response.data, response.status_code, context)
        return response

    if isinstance(exc, ObjectDoesNotExist):
        return Response(
            _error_payload(str(exc) or 'Resource not found.', 'not_found', context),
            status=status.HTTP_404_NOT_FOUND,
        )

    if isinstance(exc, DomainValidationError):
        return Response(
            _error_payload(
                exc.detail or 'Invalid request.',
                'invalid_request',
                context,
                exc.errors,
            ),
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, ValueError):
        return Response(
            _error_payload(str(exc) or 'Invalid request.', 'invalid_request', context),
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, IntegrityError):
        logger.warning('Database integrity conflict in API request.', exc_info=True)
        return Response(
            _error_payload(
                'The request conflicts with existing data.',
                'conflict',
                context,
            ),
            status=status.HTTP_409_CONFLICT,
        )

    return None


def _normalize_drf_error(data, status_code, context):
    if isinstance(data, dict) and set(data.keys()) <= {'detail', 'code'}:
        detail = data.get('detail', 'Request failed.')
        code = data.get('code', _default_code(status_code))
        return _error_payload(detail, code, context)

    if isinstance(data, dict) and 'detail' in data:
        return _error_payload(
            data['detail'],
            data.get('code', _default_code(status_code)),
            context,
            {key: value for key, value in data.items() if key not in ('detail', 'code')},
        )

    return _error_payload(
        'Validation error.' if status_code == status.HTTP_400_BAD_REQUEST else 'Request failed.',
        _default_code(status_code),
        context,
        data,
    )


def _default_code(status_code):
    if status_code == status.HTTP_400_BAD_REQUEST:
        return 'validation_error'
    if status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN):
        return 'permission_denied'
    if status_code == status.HTTP_404_NOT_FOUND:
        return 'not_found'
    if status_code == status.HTTP_409_CONFLICT:
        return 'conflict'
    return 'api_error'
