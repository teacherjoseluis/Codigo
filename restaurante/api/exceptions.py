import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


logger = logging.getLogger(__name__)


def domain_exception_handler(exc, context):
    """Map domain-layer exceptions to stable API error responses."""
    response = exception_handler(exc, context)
    if response is not None:
        return response

    if isinstance(exc, ObjectDoesNotExist):
        return Response(
            {'detail': str(exc) or 'Resource not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if isinstance(exc, ValueError):
        return Response(
            {'detail': str(exc) or 'Invalid request.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, IntegrityError):
        logger.warning('Database integrity conflict in API request.', exc_info=True)
        return Response(
            {'detail': 'The request conflicts with existing data.'},
            status=status.HTTP_409_CONFLICT,
        )

    return None
