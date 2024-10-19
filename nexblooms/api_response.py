from rest_framework.response import Response
from rest_framework import status

# *************************************
# APP Response
# *************************************

def http_500_response_app(error, message="", data=None):
    """
    Handles the response for a 500 Internal Server Error specific to the app.

    Parameters:
    - error: The error message or details.
    - message: Optional message to include in the response.
    - data: Optional data to include in the response.

    Returns:
    - A Response object with status 500.
    """
    context = {
        "status": False,
        "status_code": 500,
        "message": "Something Went Wrong!",
        "error": error,
        "data": data
    }
    return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def http_400_response_app(message, error="", data=None):
    """
    Handles the response for a 400 Bad Request specific to the app.

    Parameters:
    - message: The message to include in the response.
    - error: Optional error message or details.
    - data: Optional data to include in the response.

    Returns:
    - A Response object with status 200 (commonly used for failed requests in some apps).
    """
    context = {
        "status": False,
        "status_code": 400,
        "message": message,
        "error": error,
        "data": data
    }
    return Response(context, status=status.HTTP_200_OK)

def http_201_response_app(message, error="", data=None):
    """
    Handles the response for a 201 Created status specific to the app.

    Parameters:
    - message: The message to include in the response.
    - error: Optional error message or details.
    - data: Optional data to include in the response.

    Returns:
    - A Response object with status 200.
    """
    context = {
        "status": True,
        "status_code": 201,
        "message": message,
        "error": error,
        "data": data
    }
    return Response(context, status=status.HTTP_200_OK)

# *************************************
# Common Response
# *************************************

def http_200_response(message, error="", data=""):
    """
    Handles the response for a standard 200 OK status.

    Parameters:
    - message: The message to include in the response.
    - error: Optional error message or details.
    - data: Optional data to include in the response.

    Returns:
    - A Response object with status 200.
    """
    context = {
        "status": True,
        "status_code": 200,
        "message": message,
        "error": error,
        "data": data
    }
    return Response(context, status=status.HTTP_200_OK)

def http_200_response_pagination(message, error="", data=""):
    """
    Handles the response for a 200 OK status with pagination.

    Parameters:
    - message: The message to include in the response.
    - error: Optional error message or details.
    - data: Optional paginated data to include in the response.

    Returns:
    - A Response object with status 200.
    """
    context = {
        "status": True,
        "status_code": 200,
        "message": message,
        "error": error,
        "data": data
    }
    return Response(context, status=status.HTTP_200_OK)

def http_200_response_pagination_app(message, error="", data=[]):
    """
    Handles the response for a 200 OK status with pagination, specific to the app.

    Parameters:
    - message: The message to include in the response.
    - error: Optional error message or details.
    - data: Optional paginated data to include in the response (default is an empty list).

    Returns:
    - A Response object with status 200.
    """
    context = {
        "status": True,
        "status_code": 200,
        "message": message,
        "error": error,
        "data": data
    }
    return Response(context, status=status.HTTP_200_OK)

def http_500_response(error, message="", data=""):
    """
    Handles the response for a 500 Internal Server Error.

    Parameters:
    - error: The error message or details.
    - message: Optional message to include in the response.
    - data: Optional data to include in the response.

    Returns:
    - A Response object with status 500.
    """
    context = {
        "status": False,
        "status_code": 500,
        "message": "Something Went Wrong!",
        "error": error,
        "data": data
    }
    return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# *************************************
# WEB Response
# *************************************

def http_201_response(message, error="", data=""):
    """
    Handles the response for a 201 Created status for web responses.

    Parameters:
    - message: The message to include in the response.
    - error: Optional error message or details.
    - data: Optional data to include in the response.

    Returns:
    - A Response object with status 201.
    """
    context = {
        "status": True,
        "status_code": 201,
        "message": message,
        "error": error,
        "data": data
    }
    return Response(context, status=status.HTTP_201_CREATED)

def http_400_response(message, error="", data=""):
    """
    Handles the response for a 400 Bad Request for web responses.

    Parameters:
    - message: The message to include in the response.
    - error: Optional error message or details.
    - data: Optional data to include in the response.

    Returns:
    - A Response object with status 400.
    """
    context = {
        "status": False,
        "status_code": 400,
        "message": message,
        "error": error,
        "data": data
    }
    return Response(context, status=status.HTTP_400_BAD_REQUEST)

def http_400_response_app(message, error="", data=None):
    """
    Handles the response for a 400 Bad Request specific to the app but returns status 200.

    Parameters:
    - message: The message to include in the response.
    - error: Optional error message or details.
    - data: Optional data to include in the response.

    Returns:
    - A Response object with status 200.
    """
    context = {
        "status": False,
        "status_code": 200,  # Status code is 200 despite being a bad request
        "message": message,
        "error": error,
        "data": data
    }
    return Response(context, status=status.HTTP_200_OK)

def http_200_response_app(message, error="", data=None):
    """
    Handles the response for a standard 200 OK status specific to the app.

    Parameters:
    - message: The message to include in the response.
    - error: Optional error message or details.
    - data: Optional data to include in the response.

    Returns:
    - A Response object with status 200.
    """
    context = {
        "status": True,
        "status_code": 200,
        "message": message,
        "error": error,
        "data": data
    }
    return Response(context, status=status.HTTP_200_OK)
