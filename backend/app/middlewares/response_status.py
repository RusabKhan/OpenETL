from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class StatusAdjustMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """
        Dispatch the incoming request and adjust the HTTP response based on the request path.
        
        Parameters:
            request (Request): The incoming HTTP request.
            call_next (Callable[[Request], Awaitable[Response]]): A callable that processes the request through the next middleware or endpoint and returns a Response.
        
        Returns:
            Response: The HTTP response after potential modifications to its status code and body.
        
        This asynchronous method awaits a response from the next handler by calling call_next(request). It then inspects the request URL path (converted to lowercase) to determine if specific keywords ("get", "create", "update", "delete") are present:
            - If "get" is in the path and the status code is 200, the response remains unchanged.
            - If "create" is in the path, the response status code is set to 201 (Created).
            - If "update" is in the path, the response status code is set to 204 (No Content), the response body is cleared, and the "content-length" header is set to "0".
            - If "delete" is in the path, the response status code is set to 202 (Accepted).
        
        The modified response is then returned.
        """
        response: Response = await call_next(request)

        path = request.url.path.lower()

        if "get" in path and response.status_code == 200:
            pass
        elif "create" in path:
            response.status_code = 201
        elif "update" in path:
            response.status_code = 204  # No Content
            response.body = b""  # Empty body
            response.headers["content-length"] = "0"  # Ensure content-length is 0
        elif "delete" in path:
            response.status_code = 202  # Accepted

        return response
