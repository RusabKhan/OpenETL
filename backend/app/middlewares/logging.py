from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
import sys
import os
from openetl_utils.logger import get_logger

LOG_FILE = f"{os.environ['OPENETL_HOME']}/.logs/api.log"


logger = get_logger(name="api", log_file=LOG_FILE)

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log incoming HTTP requests and their corresponding responses.

    Parameters:
        request (Request): The incoming HTTP request.
        call_next (Callable[[Request], Awaitable[Response]]): A callable that processes the request through the next middleware or endpoint and returns a Response.

    Logs:
        - The HTTP method and URL of the request.
        - The headers and body of the request.
        - The status code and body of the response.

    Exceptions:
        Logs any exceptions that occur during request processing and re-raises them.

    Returns:
        Response: The HTTP response after logging and potential modifications to its body.
    """
    async def dispatch(self, request: Request, call_next):
        try:
            logger.info("LoggingMiddleware: Processing request")

            body = await request.body()
            logger.info(f"Request: {request.method} {request.url}")
            logger.info(f"Headers: {dict(request.headers)}")
            logger.info(f"Body: {body.decode('utf-8') if body else 'No body'}")

            response = await call_next(request)

            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk

            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response body: {response_body.decode('utf-8')}")

            async def new_body_iterator():
                yield response_body

            response.body_iterator = new_body_iterator()

            return response

        except Exception as exc:
            logger.error("An exception occurred during request processing", exc_info=True)
            raise




class LoggerStream:
    def write(self, message):
        if message.strip():  # Avoid blank lines
            logger.info(message.strip())

    def flush(self):
        pass

sys.stdout = LoggerStream()
sys.stderr = LoggerStream()

