from rest_framework.response import Response
from rest_framework import status

def api_response(success=True, data=None, message="", status_code=status.HTTP_200_OK):
    """
    Standardized API response format.
    """
    return Response(
        {
            "success": success,
            "data": data,
            "message": message,
        },
        status=status_code,
    )

def api_error(message="An error occurred", status_code=status.HTTP_400_BAD_REQUEST, data=None):
    """
    Standardized API error format.
    """
    return api_response(success=False, data=data, message=message, status_code=status_code)
