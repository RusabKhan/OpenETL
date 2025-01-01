from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import traceback
import sys
from sqlalchemy.exc import (
    IntegrityError,
    NoResultFound,
    MultipleResultsFound,
    OperationalError,
    ProgrammingError,
    SQLAlchemyError,
)
from functools import wraps


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except NoResultFound:
            return await self.handle_exception(f"No result found for the given query", request, 404)
        except MultipleResultsFound:
            return await self.handle_exception("Multiple results found where one was expected.", request, 400)
        except IntegrityError as exc:
            return await self.handle_exception(f"Database integrity error: {str(exc.orig)}", request, 409)
        except OperationalError as exc:
            return await self.handle_exception(f"Operational error occurred: {str(exc.orig)}", request, 500)
        except ProgrammingError as exc:
            return await self.handle_exception(f"Programming error: {str(exc.orig)}", request, 400)
        except SQLAlchemyError as exc:
            return await self.handle_exception(f"A general Database error occurred: {str(exc)}", request, 500)
        except ValueError as exc:
            return await self.handle_exception(exc, request, 400)
        except HTTPException as exc:
            return await self.handle_exception(exc, request, exc.status_code)
        except Exception as exc:
            return await self.handle_exception(exc, request, 500)

    async def handle_exception(self, exc, request, status_code):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        trace = traceback.extract_tb(exc_traceback)

        error_message = str(exc)
        api_details = f"{request.method} {request.url}"
        trace_info = {
            "filename": trace[-1].filename if trace else "N/A",
            "line": trace[-1].lineno if trace else "N/A",
            "function": trace[-1].name if trace else "N/A",
        }

        print(f"Error: {error_message}")
        print(f"API: {api_details}")
        print(f"Trace: {trace_info}")

        error_response = {
            "error": "An exception occurred",
            "status_code": status_code,
            "message": error_message,
            "api_call": api_details,
            "trace": trace_info,
        }
        return JSONResponse(status_code=status_code, content=error_response)


