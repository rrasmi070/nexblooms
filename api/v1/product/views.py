from api.v1.account.thread import *
from api.v1.product.serializer import *
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from api.v1.product.utils import *
from api.v1.models import *
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import filters
from rest_framework import parsers
from api.v1.product.utils import SearchCategoryRecord
from nexblooms.paginations import CustomPagination, NexbloomsDefaultPaginationClass
import django_filters.rest_framework
import pandas as pd
import numpy as np
import json
from django.db import transaction
from rest_framework import permissions
from nexblooms.settings import IMAGE_SIZE
from nexblooms.api_response import *
from nexblooms.messages import *
import datetime
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from nexblooms.permissions import *




class CategoryListViewset(ModelViewSet):
    serializer_class = GetCategoryListSerializer
    permission_classes = (permissions.IsAuthenticated,)   
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        queryset = ProductCategory.objects.filter(is_deleted=False,is_active=True).all().order_by('name')
        serializer = GetCategoryListSerializer(queryset, many=True)
        return http_200_response_pagination(message=FOUND,data=serializer.data)
    

class CategoryMasterViewset(ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticated,AccessToProductCategory)
    filter_backends = [filters.SearchFilter]
    search_fields = ['category_name']
    http_method_names = [ "get", "put", "delete","post"]
    parser_classes = [parsers.FormParser, parsers.MultiPartParser]

    
    def get_serializer_class(self):
        if self.action == 'create':
            return CategoryRegisterSerializer
        if self.action in ["list","retrieve"]:
            return self.serializer_class
        
        elif self.action == "update":
            return  CategoryUpdateSerializer
        
        else:
            return self.serializer_class
    
    def create(self,request):
        try:
            serializer = CategoryRegisterSerializer(data=request.data,context={"user":request.user})
            if serializer.is_valid():
                serializer.save()
                data = serializer.data
                return http_201_response(message=CATEGORY_CREATE)
            else:
                if list(serializer.errors.keys())[0] != "error":
                    return http_400_response(message=f"{list(serializer.errors.keys())[0]} : {serializer.errors[list(serializer.errors.keys())[0]][0]}")
                else:
                    return http_400_response(message=serializer.errors[list(serializer.errors.keys())[0]][0])
        except Exception as e:
            return http_500_response(error=str(e))


        
    search = openapi.Parameter('search',in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)
    status = openapi.Parameter('status',in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)
    @swagger_auto_schema(manual_parameters=[status,search])
    def list(self, request, *args, **kwargs):
        search = self.request.query_params.get('search')
        status = self.request.query_params.get('status')
        queryset = ProductCategory.objects.filter(is_deleted=False)
        if status is None:
            queryset = queryset.order_by('-created_on').values('id', 'name', 'description',"image",'is_active')
        elif status.lower() == "active":
            queryset = queryset.filter(is_active=True).order_by('-created_on').values('id', 'name', 'description',"image",'is_active')
        elif status.lower() == "inactive":
            queryset = queryset.filter(is_active=False).order_by('-created_on').values('id', 'name', 'description',"image",'is_active')
        else:
            queryset = queryset.order_by('-created_on').values('id', 'name', 'description',"image",'is_active')
        if queryset:
            # try:
            category_list_dataframe = pd.DataFrame(queryset)
            category_list_dataframe['image'] = category_list_dataframe['image'].apply(lambda x: (str(request.build_absolute_uri('/'))[:-1] + "/media/" + x) if x else '')

            if search:
                search = re.escape(search)
                search = search.strip()
                category_list_dataframe = SearchCategoryRecord(category_list_dataframe, search)
            category_list_json = category_list_dataframe.to_json(orient='records')
            category_list_json = json.loads(category_list_json)
            paginator = NexbloomsDefaultPaginationClass()
            result_page = paginator.paginate_queryset(category_list_json, request)
            return paginator.get_paginated_response(result_page)
        return http_200_response_pagination(message=NOT_FOUND)

            
    def retrieve(self,request,pk):
        try:
            data = ProductCategory.objects.filter(id=pk).last()
            if data:
                serializer_data = CategorySerializer(data,many=False)
                if serializer_data:
                    return http_200_response(message=FOUND,data=serializer_data.data)
                else:
                    return http_400_response(message=NOT_FOUND)
            else:
                return http_200_response(message=NOT_FOUND)
        except Exception as e:
            return http_500_response(error=str(e))

    def destroy(self, request,pk):
        try:
            data = ProductCategory.objects.filter(id=pk).last()
            if data:
                obj=data
                obj.is_deleted=True
                obj.save()
                return http_200_response(message=CATEGORY_DELETE)
            else:
                return http_400_response(message=NOT_FOUND)
        except Exception as e:
            return http_500_response(error=str(e))
            


    def update(self,request,pk):
        try:
            user_obj=ProductCategory.objects.filter(id=pk).last()
            serializer = CategoryUpdateSerializer(data=request.data,context={'request':request,"user_obj":user_obj,"user":request.user})
            if serializer.is_valid():
                return http_200_response(message=CATEGORY_UPDATE)
            else:
                if list(serializer.errors.keys())[0] != "error":
                    return http_400_response(message=f"{list(serializer.errors.keys())[0]} : {serializer.errors[list(serializer.errors.keys())[0]][0]}")
                else:
                    return http_400_response(message=serializer.errors[list(serializer.errors.keys())[0]][0])
        except Exception as e:
            return http_500_response(error=str(e))   
    


class ActiveInactiveCategoryViewset(ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,AccessToProductCategory)
    serializer_class = ActiveInactiveCategorySerializer
    http_method_names = ['put']

    def update(self, request, pk):
        if pk:
            try:
                category_check = ProductCategory.objects.get(id=pk)
            except ProductCategory.DoesNotExist:
                return http_400_response(message=NO_CATEGORY)

            serializer = ActiveInactiveCategorySerializer(
                instance=category_check,
                data=request.data,
                context={'request': request}
            )
            if serializer.is_valid():
                category_check.is_active = request.data['is_active']
                category_check.save()
                if request.data['is_active']:
                    return http_200_response(message=ACTIVE)
                else:
                    return http_200_response(message=INACTIVE)
            else:
                error_key = next(iter(serializer.errors.keys()))
                error_message = serializer.errors[error_key][0]
                return http_400_response(message=f"{error_key}: {error_message}")

        else:
            return http_400_response(message=CATEGORY_ID)

class ProductManagement(ModelViewSet):
    serializer_class = CreateProductSerializer
    # permission_classes = (permissions.IsAuthenticated)   
    parser_classes = [parsers.FormParser, parsers.MultiPartParser]
    filter_backends = [filters.SearchFilter,django_filters.rest_framework.DjangoFilterBackend]
    search_fields = ['product_name']
    # http_method_names = ['post'],'put'
    http_method_names = ['get','post','delete']
 
    def get_serializer_class(self):
        if self.action == "create":
            return CreateProductSerializer
        # elif self.action == "retrieve":
        #     return GetproductMasterSerializer
        # else:
        #     return self.serializer_class
    
    def get_queryset(self):
        product_obj = ProductMaster.objects.filter(is_deleted=False).all().order_by('-created_on')
        return product_obj

        
    def create(self, request, *args, **kwargs):
        # try:
            serializer = CreateProductSerializer(data = request.data, context={'request':request})
            
            # with transaction.atomic():
            if serializer.is_valid():
                mkdir=ProductMaster.objects.latest('created_on')
                # serializer_show=ShowGetproductMasterSerializer(mkdir,context={'request':request})
                return http_201_response(message=PRODUCT_CREATE,data="serializer_show.data")
            else:
                if list(serializer.errors.keys())[0] != "error":
                    return http_400_response(message=f"{list(serializer.errors.keys())[0]} : {serializer.errors[list(serializer.errors.keys())[0]][0]}")
                else:
                    return http_400_response(message=serializer.errors[list(serializer.errors.keys())[0]][0])
        # except Exception as e:
        #     return http_500_response(error=str(e))


    status = openapi.Parameter('status',in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)
    @swagger_auto_schema(manual_parameters=[status])
    def list(self, request, *args, **kwargs):
            search = self.request.query_params.get('search')
            status = self.request.query_params.get('status')

            queryset = self.get_queryset().values('id','sku_id','name','product_category__name','product_category','stock_quantity','price','is_active').order_by('-created_on')
            
            if status=="active":
                queryset=queryset.filter(is_active=True).all().order_by('-created_on')
            elif status=="inactive":
                queryset=queryset.filter(is_active=False).all().order_by('-created_on')
            else:
                queryset=queryset

            if queryset:
                product_dataframe = pd.DataFrame(queryset)
                product_images_mapping_df = pd.DataFrame(ProductImageMapping.objects.all().values('product_id', 'product_image'))

                if search:
                # try:
                    search=search.strip()
                    search=re.escape(search)
                    product_dataframe = SearchProductRecord(product_dataframe, search)
                # except:
                #     product_dataframe = pd.DataFrame()
        
                product_dataframe = product_dataframe.rename(columns={'product_category__name': 'product_category_name', 'name': 'product_name'})
                
                product_dataframe=product_dataframe.fillna("")
                product_json = product_dataframe.to_json(orient='records')
                product_json = json.loads(product_json)
                paginator = NexbloomsDefaultPaginationClass()
                # paginator.page_size = page_size
                result_page = paginator.paginate_queryset(product_json, request)
                return paginator.get_paginated_response(result_page)
            return http_200_response_pagination(message=NOT_FOUND)


    def retrieve(self, request, pk=None):
        try:
            product_obj = ProductMaster.objects.filter(id=pk).values('id','sku_id','name','product_category__name','product_category','stock_quantity','price','is_active').order_by('-created_on')

            if product_obj:
                product_dataframe = pd.DataFrame(product_obj)
                product_json = product_dataframe.to_json(orient='records')
                parsed_data = json.loads(product_json)
                return http_200_response(message=FOUND,data=parsed_data)
            else:
                return http_200_response(message=NOT_FOUND)
        except Exception as e:
            return http_500_response(error=str(e))

    def destroy(self, request, pk=None):
        if pk:
            product = ProductMaster.objects.filter(id=pk, is_deleted=False).last()
            if product:
                product.is_deleted=True
                product.save()
                Cart.objects.filter(product_id=pk).delete()
                WishlistMaster.objects.filter(product_id=pk).delete()
                return http_200_response(message=PRODUCT_DELETE)
            else:
                return http_400_response(message=NO_PRODUCT)
        else:
            return http_400_response(message=PRODUCT_ID)


    # def update(self, request, pk ,*args, **kwargs):
    #     try:
    #         instance = ProductMaster.objects.filter(id=int(pk)).last()
    #         if not instance:
    #             return http_400_response(message=NOT_FOUND)
    #         serialized_data = UpdateProductMasterSerializer(instance,request.data,context={'user':request.user,'request':request})
    #         if serialized_data.is_valid():
    #             return http_200_response(message=PRODUCT_UPDATE)
    #         else:
    #             if list(serialized_data.errors.keys())[0] != "error":
    #                 return http_400_response(message=f"{list(serialized_data.errors.keys())[0]} : {serialized_data.errors[list(serialized_data.errors.keys())[0]][0]}")
    #             else:
    #                 return http_400_response(message=serialized_data.errors[list(serialized_data.errors.keys())[0]][0])
    #     except Exception as e:
    #         return http_500_response(error=str(e))
