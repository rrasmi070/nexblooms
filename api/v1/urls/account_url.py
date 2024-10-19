from rest_framework.routers import DefaultRouter
from api.v1.account.views import *
from django.urls import path, include
from django.contrib import admin

from api.v1.products.views import BrandGenerics, CategoryGenerics, ProductsDetailsGenerics, ProductsGenerics


router = DefaultRouter()

router.register('account/web_register', WebUserRegisterViewset, basename='web_register')



urlpatterns = [
    path('', include(router.urls)),
    path('account/login/', UserMobileLoginGenerics.as_view(),name='mobile_login'),
    path('product/bands/', BrandGenerics.as_view(),name='bradn_list'),
    path('product/category/', CategoryGenerics.as_view(),name='category'),
    path('product/products/', ProductsGenerics.as_view(),name='products'),
    path('product/product-details/', ProductsDetailsGenerics.as_view(),name='product-details'),
    
    
    # path('change_password_confirmation/<str:token>', ChangePasswordConfirmationGenerics.as_view(),name='change_password_confirmation'),
    # path('change_password_confirmation', ChangePasswordConfirmationGenerics.as_view(),name='change_password_confirmation')
]


