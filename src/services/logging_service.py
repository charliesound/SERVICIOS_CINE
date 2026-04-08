import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(name: str = "servicios_cine", level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    file_handler = RotatingFileHandler(
        log_dir / "app.log", maxBytes=10_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


class RequestLogger:
    def __init__(self, logger_name: str = "requests"):
        self.logger = logging.getLogger(logger_name)

    def log_request(
        self,
        method: str,
        path: str,
        user_id: str = None,
        status: int = None,
        duration_ms: float = None,
    ):
        msg = f"{method} {path}"
        if user_id:
            msg += f" | user={user_id}"
        if status:
            msg += f" | status={status}"
        if duration_ms is not None:
            msg += f" | {duration_ms:.1f}ms"

        if status and status >= 500:
            self.logger.error(msg)
        elif status and status >= 400:
            self.logger.warning(msg)
        else:
            self.logger.info(msg)


class ErrorTracker:
    def __init__(self, logger_name: str = "errors"):
        self.logger = logging.getLogger(logger_name)
        self._error_counts: dict = {}

    def track_error(self, error: Exception, context: dict = None):
        error_type = type(error).__name__
        self._error_counts[error_type] = self._error_counts.get(error_type, 0) + 1

        msg = f"Error: {error_type} - {str(error)}"
        if context:
            msg += f" | context={context}"

        self.logger.error(msg, exc_info=True)

    def get_stats(self) -> dict:
        return {
            "total_errors": sum(self._error_counts.values()),
            "by_type": dict(self._error_counts),
        }


logger = setup_logging()
request_logger = RequestLogger()
error_tracker = ErrorTracker()
