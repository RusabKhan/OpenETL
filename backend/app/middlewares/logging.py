import logging
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
import sys
import os

LOG_FILE = f"{os.environ['OPENETL_HOME']}/.logs/api.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),  # Log to a file
        logging.StreamHandler()          # Optionally, also log to console
    ]
)

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

# Console handler for logging to console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)

# Add both handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

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

