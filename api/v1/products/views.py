from rest_framework import generics, status, permissions
from api.v1.models import *
from rest_framework.response import Response
## Swagger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import FormParser, MultiPartParser

from api.v1.products.serializer import ProductsAddSerializer, ProductsAllSerializer


class CategoryGenerics(generics.GenericAPIView):
    def get(self, *args, **kwargs):
        res = Category.objects.filter(status = True).values()
        context = {'status': True,'message': res}
        return Response(context, status=status.HTTP_200_OK)


class BrandGenerics(generics.GenericAPIView):
    def get(self, *args, **kwargs):
        res = Brands.objects.filter(status = True).values()
        context = {'status': True,'message': res}
        return Response(context, status=status.HTTP_200_OK)
        
        
class AddProductsGenerics(generics.GenericAPIView):
    serializer_class = ProductsAddSerializer
    parser_classes = (FormParser, MultiPartParser)
        
    def post(self, *args, **kwargs):
        serializer = ProductsAddSerializer(data=self.request.data)
        if serializer.is_valid():
            serializer.save()
            context = {'status': True,'message': 'Product created successfully','data': serializer.data}
            return Response(context, status=status.HTTP_200_OK)
        else:
            context = {'status': False,'message': serializer.errors}
            return Response(context, status=status.HTTP_200_OK)
    

class ProductsGenerics(generics.GenericAPIView):
    serializer_class = ProductsAllSerializer
    brand_id_param_config = openapi.Parameter('brand_id',in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)
    @swagger_auto_schema(manual_parameters=[brand_id_param_config])
    def get(self, *args, **kwargs):
        brand_id = self.request.query_params.get('brand_id', None)
        if brand_id:
            res = Products.objects.filter(status = True, brand_name = brand_id)
        else:
            res = Products.objects.filter(status = True)
        serializer = self.serializer_class(res, many=True)
        context = {'status': True,'message': serializer.data}
        return Response(context, status=status.HTTP_200_OK)
    

class ProductsDetailsGenerics(generics.GenericAPIView):
    serializer_class = ProductsAllSerializer
    priduct_id_param_config = openapi.Parameter('priduct_id',in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)
    @swagger_auto_schema(manual_parameters=[priduct_id_param_config])
    def get(self, *args, **kwargs):
        priduct_id = self.request.query_params.get('priduct_id', None)
        res = Products.objects.filter(status = True, id = priduct_id).last()
        serializer = self.serializer_class(res, many=False)
        
        context = {'status': True,'message': serializer.data}
        return Response(context, status=status.HTTP_200_OK)
        

    
    