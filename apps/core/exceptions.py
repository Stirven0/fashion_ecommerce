from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status


class ServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'


class InsufficientStock(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Insufficient stock for this operation.'
    default_code = 'insufficient_stock'


class InvalidCartOperation(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid cart operation.'
    default_code = 'invalid_cart'


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        response.data['status_code'] = response.status_code
        
    return response

