import time
from http import HTTPStatus
from api.utils.logger import logger


class LoggingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope["path"]
        method = scope["method"]

        if path == "/favicon.ico":
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()
        status_code = 500

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            status = HTTPStatus(status_code)

            logger_method = logger.info
            if status_code >= 500:
                logger_method = logger.error
            elif status_code >= 400:
                logger_method = logger.warning

            logger_method(
                f"{status.value} {status.phrase}",
                extra={
                    "req": {"method": method, "path": path},
                    "res": {"status_code": status.value, "status_text": status.phrase, "duration_ms": duration_ms},
                },
            )
        except Exception:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.error(
                "Unhandled exception",
                extra={
                    "req": {"method": method, "path": path},
                    "res": {"status_code": 500, "status_text": "Internal Server Error", "duration_ms": duration_ms},
                },
                exc_info=True
            )
            raise
