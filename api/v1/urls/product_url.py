from rest_framework.routers import DefaultRouter
from api.v1.product.views import *
from django.urls import path, include
from django.contrib import admin


router = DefaultRouter()

router.register('category_list_dropdown', CategoryListViewset, basename='category_list')
router.register('category_management', CategoryMasterViewset, basename='category_management')
router.register('active_inactive_category', ActiveInactiveCategoryViewset, basename='active_inactive_category')
router.register('product_management', ProductManagement, basename='product_management') #product managment api



urlpatterns = [
    path('', include(router.urls)),
]


