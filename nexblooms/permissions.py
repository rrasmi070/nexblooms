from rest_framework import permissions
from rest_framework.exceptions import APIException
from rest_framework import status
from django.db.models import Q
from api.v1.models import *


class NeedAccess(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {'status': bool(False), 'message':'You do not have permission to this module' }
    default_code = 'not_authenticated'



# category 
class AccessToProductCategory(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role_id==3 or request.user.role_id==1:
            if request.method == "GET":
                return request.user
            
            elif request.method == "POST" or request.method == "PUT" or request.method == "DELETE":
                if request.user.role_id==1:
                    return request.user
                else:
                    raise NeedAccess()
            else:
                raise NeedAccess()
        else:
            return request.user