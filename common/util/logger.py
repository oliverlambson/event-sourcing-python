import structlog
import traceback
from typing import Any, Dict, Optional

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)


class Logger:
    def __init__(self):
        self._logger = structlog.get_logger()

    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        self._logger.debug(message, **(context or {}))

    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        self._logger.info(message, **(context or {}))

    def warn(self, message: str, error: Optional[Exception] = None, context: Optional[Dict[str, Any]] = None) -> None:
        error_context = {}
        if error:
            error_context = {
                "error": {
                    "message": str(error),
                    "stack": traceback.format_exc(),
                }
            }

        self._logger.warning(message, **(error_context | (context or {})))

    def error(self, message: str, error: Optional[Exception] = None, context: Optional[Dict[str, Any]] = None) -> None:
        error_context = {}
        if error:
            error_context = {
                "error": {
                    "message": str(error),
                    "stack": traceback.format_exc(),
                }
            }

        self._logger.error(message, **(error_context | (context or {})))


# Global logger instance
log = Logger()
