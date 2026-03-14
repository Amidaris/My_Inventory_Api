import logging
from logging.handlers import TimedRotatingFileHandler
import json
from api.config.settings import settings
from asgi_correlation_id import correlation_id

LOG_DIR_PATH = settings.LOG_DIR
LOG_FILE = f"{LOG_DIR_PATH}/api.json"
BACKUP_COUNT = settings.LOG_BACKUP_COUNT
LOG_LEVEL = settings.LOG_LEVEL


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "timestamp": self.formatTime(record, datefmt="%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # Get correlation_id from ContextVar
        log["correlation_id"] = correlation_id.get() or "-"

        if hasattr(record, "req"):
            log["req"] = record.req
        if hasattr(record, "res"):
            log["res"] = record.res
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)

        return json.dumps(log, ensure_ascii=False)


logger = logging.getLogger("api")
logger.setLevel(LOG_LEVEL)

file_handler = TimedRotatingFileHandler(
    LOG_FILE,
    when="midnight",
    interval=1,
    backupCount=BACKUP_COUNT,
    encoding="utf-8"
)
file_handler.setFormatter(JsonFormatter())
logger.addHandler(file_handler)
logger.propagate = False
