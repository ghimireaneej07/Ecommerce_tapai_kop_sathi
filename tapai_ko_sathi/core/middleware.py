import logging
import traceback
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware:
    """
    Catch-all middleware to handle exceptions and return standardized JSON 
    responses if the request starts with /api/.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            return self.handle_exception(request, e)

    def process_exception(self, request, exception):
        return self.handle_exception(request, exception)

    def handle_exception(self, request, exception):
        logger.exception("Unhandled exception occurred: %s", exception)
        
        if request.path.startswith("/api/"):
            data = {
                "success": False,
                "message": "Internal Server Error",
            }
            if settings.DEBUG:
                data["error_detail"] = str(exception)
                data["traceback"] = traceback.format_exc()
            
            return JsonResponse(data, status=500)
        
        # For non-API requests, let Django handle it with default 500 handler
        # unless we want a custom page override here.
        return None
