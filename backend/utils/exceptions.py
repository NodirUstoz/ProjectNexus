"""
Custom exception handler for consistent API error responses.
"""

import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error response format:
    {
        "error": True,
        "status_code": 400,
        "message": "Human-readable error message",
        "errors": { ... }  // Field-level errors for validation failures
    }
    """
    # Convert Django validation errors to DRF validation errors
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, "message_dict"):
            exc = ValidationError(detail=exc.message_dict)
        else:
            exc = ValidationError(detail=exc.messages)

    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            "error": True,
            "status_code": response.status_code,
        }

        if isinstance(exc, ValidationError):
            error_data["message"] = "Validation failed."
            error_data["errors"] = response.data
        elif isinstance(exc, Http404):
            error_data["message"] = "Resource not found."
        elif isinstance(exc, APIException):
            error_data["message"] = str(exc.detail)
        else:
            error_data["message"] = "An error occurred."

        response.data = error_data
    else:
        # Unhandled exceptions - log and return 500
        logger.exception(
            f"Unhandled exception in {context.get('view', 'unknown view')}",
            exc_info=exc,
        )
        response = Response(
            {
                "error": True,
                "status_code": 500,
                "message": "An internal server error occurred.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response


class ConflictError(APIException):
    """409 Conflict - raised when an action conflicts with existing state."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "This action conflicts with the current state."
    default_code = "conflict"


class RateLimitExceeded(APIException):
    """429 Too Many Requests."""

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = "Rate limit exceeded. Please try again later."
    default_code = "rate_limit_exceeded"
