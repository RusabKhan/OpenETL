from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import traceback
import sys

class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            # Process the request normally
            return await call_next(request)
        except Exception as exc:
            # Extract exception details
            exc_type, exc_value, exc_traceback = sys.exc_info()
            trace = traceback.extract_tb(exc_traceback)

            # Prepare the error response
            error_message = str(exc)
            api_details = f"{request.method} {request.url}"
            trace_info = {
                "filename": trace[-1].filename if trace else "N/A",
                "line": trace[-1].lineno if trace else "N/A",
                "function": trace[-1].name if trace else "N/A",
            }

            # Log error details (optional)
            print(f"Error: {error_message}")
            print(f"API: {api_details}")
            print(f"Trace: {trace_info}")

            # Determine status code
            status_code = 500
            if isinstance(exc, HTTPException):
                status_code = exc.status_code

            # Format response
            error_response = {
                "error": "An exception occurred",
                "status_code": status_code,
                "message": error_message,
                "api_call": api_details,
                "trace": trace_info,
            }
            return JSONResponse(status_code=status_code, content=error_response)
