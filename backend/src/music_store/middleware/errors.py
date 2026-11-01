import logging

from starlette.responses import JSONResponse

from music_store.errors import DomainError

logger = logging.getLogger(__name__)

UNEXPECTED_ERROR_DETAIL = "Unexpected error."


def error_response(error: Exception) -> JSONResponse:
    """Map a DomainError to its own response and anything else to a generic, logged 500."""
    if isinstance(error, DomainError):
        return JSONResponse({"detail": error.detail}, status_code=error.status_code)
    logger.error("Unexpected error in middleware", exc_info=error)
    return JSONResponse({"detail": UNEXPECTED_ERROR_DETAIL}, status_code=500)
