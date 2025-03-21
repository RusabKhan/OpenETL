from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class StatusAdjustMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        path = request.url.path.lower()

        if 200 <= response.status_code < 300:
            if "get" in path and response.status_code == 200:
                pass  # Keep as 200
            elif "create" in path:
                response.status_code = 201
            elif "update" in path:
                response.status_code = 204  # No Content
                response.body = b""  # Empty body
                response.headers["content-length"] = "0"
            elif "delete" in path:
                response.status_code = 202  # Accepted

        return response
