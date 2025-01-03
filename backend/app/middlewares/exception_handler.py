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
from psycopg2.errors import UniqueViolation, ForeignKeyViolation, SerializationFailure, DeadlockDetected
from sqlalchemy.exc import DBAPIError
import re


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except NoResultFound:
            return await self.handle_exception(f"No result found for the given query", request, 404)
        except MultipleResultsFound:
            return await self.handle_exception("Multiple results found where one was expected.", request, 400)
        except IntegrityError as exc:
            # Handling specific integrity errors such as duplicate keys
            if isinstance(exc.orig, UniqueViolation):
                key_name, value = self.extract_key_details(exc.orig)
                return await self.handle_exception(
                    f"Duplicate {key_name.replace('_', ' ')}: {value}.",
                    request, 409)
            if isinstance(exc.orig, ForeignKeyViolation):
                key_name, value = self.extract_key_details(exc.orig)
                return await self.handle_exception(
                    f"No such {key_name.replace('_', ' ')}: {value}.", request,
                    409)
            return await self.handle_exception(f"Database integrity error: {str(exc.orig)}", request, 409)
        except OperationalError as exc:
            return await self.handle_exception(f"Operational error occurred: {str(exc.orig)}", request, 500)
        except ProgrammingError as exc:
            return await self.handle_exception(f"Programming error: {str(exc.orig)}", request, 400)
        except TimeoutError as exc:
            return await self.handle_exception(f"Database timeout occurred: {str(exc)}. Please try again later.",
                                               request, 504)
        except SerializationFailure as exc:
            return await self.handle_exception(
                f"Transaction serialization failure: {str(exc)}. Please try again later.", request, 500)
        except DeadlockDetected as exc:
            return await self.handle_exception(f"Deadlock detected: {str(exc)}. Please try again later.", request, 409)
        except DBAPIError as exc:
            return await self.handle_exception(f"Database error: {str(exc)}. Please check the database connection.",
                                               request, 500)
        except SQLAlchemyError as exc:
            return await self.handle_exception(f"A general database error occurred: {str(exc)}", request, 500)
        except ValueError as exc:
            return await self.handle_exception(exc, request, 400)
        except HTTPException as exc:
            return await self.handle_exception(exc, request, exc.status_code)
        except Exception as exc:
            return await self.handle_exception(f"Unexpected error: {str(exc)}", request, 500)

    def extract_key_details(self, error_obj):
        """
        Helper method to extract key name and the offending value from the error message
        """
        # Check for 'key' or 'constraint' names in the error message
        # This regex matches key or constraint names in typical PostgreSQL error messages.
        key_pattern = re.compile(r'Key \((.*?)\)=(.*?)\s+')
        match = key_pattern.search(str(error_obj))
        if match:
            key_name = match.group(1)
            value = match.group(2).strip("'")  # Clean up extra quotes around values
            return key_name, value
        return "Unknown Key", "Unknown Value"

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
