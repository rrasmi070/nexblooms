from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
 
 


class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10000
        
    def get_paginated_response(self, data):
        limit = self.request.query_params.get('page_size', self.page_size)
        return Response({
            'status': True,
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'page_size':int(limit),
            'data': data
        })
        
        
class NexbloomsDefaultPaginationClass(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size =100
    message = ''
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = kwargs.get('message', '')
        
    def get_paginated_response(self, data):
        limit = self.request.query_params.get('page_size', 10)
 
        if self.page.paginator.count == 0:
            return Response({
                'status': True,
                "status_code":200,
                "message":"Data not found",
                "error":"",
                'links': {
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link()
                },
                'count': self.page.paginator.count,
                'page_size':int(limit),
                "data":data}
            )
        else:
            return Response({
                'status': True,
                "status_code":200,
                "message":self.message,
                "error":"",
                'links': {
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link()
                },
                'count': self.page.paginator.count,
                'page_size':int(limit),
                "data":data}
            )
        
class WishlistPaginationClass(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size =100
    message = ''
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = kwargs.get('message', '')
        
    def get_paginated_response(self, data):
        limit = self.request.query_params.get('page_size', 10)
 
        if self.page.paginator.count == 0:
            return Response({
                'status': True,
                "status_code":200,
                "message":"Data not found",
                "error":"",
                'links': {
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link()
                },
                'count': self.page.paginator.count,
                'page_size':int(limit),
                "data":data}
            )
        else:
            return Response({
                'status': True,
                "status_code":200,
                "message":self.message,
                "error":"",
                'links': {
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link()
                },
                'count': self.page.paginator.count,
                'page_size':int(limit),
                "data":data}
            )



class NexbloomsAppHomepageSearchDefaultPaginationClass(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size =100
    message = ''
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = kwargs.get('message', '')
        
    def get_paginated_response(self, data):
        limit = self.request.query_params.get('page_size', 15)
 
        if self.page.paginator.count == 0:
            return Response({
                'status': True,
                "status_code":200,
                "message":"Data not found",
                "error":"",
                'links': {
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link()
                },
                'count': self.page.paginator.count,
                'page_size':int(limit),
                "data":data}
            )
        else:
            return Response({
                'status': True,
                "status_code":200,
                "message":self.message,
                "error":"",
                'links': {
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link()
                },
                'count': self.page.paginator.count,
                'page_size':int(limit),
                "data":data}
            )
