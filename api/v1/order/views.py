from rest_framework import generics, status, permissions
from api.v1.models import *
from rest_framework.response import Response
## Swagger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import FormParser, MultiPartParser

from api.v1.order.serializers import OrderCreateSerializer, UserOrderSerializer


class OrderCreateGenerics(generics.GenericAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserOrderSerializer
        else:
            return OrderCreateSerializer
    
    def post(self, *args, **kwargs):
        serializer = OrderCreateSerializer(data=self.request.data)
        if serializer.is_valid():
            serializer.save()
            context = {'status': True,'message': 'Order created successfully','data': serializer.data}
            return Response(context, status=status.HTTP_200_OK)
        else:
            context = {'status': False,'message': serializer.errors}
            return Response(context, status=status.HTTP_200_OK)
    
    def get(self, *args, **kwargs):
        user = self.request.user
        res = Orders.objects.filter(status = True, user = user)
        serializer = UserOrderSerializer(res, many=True)
        context = {'status': True,'message': serializer.data}
        return Response(context, status=status.HTTP_200_OK)