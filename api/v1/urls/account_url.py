from rest_framework.routers import DefaultRouter
from api.v1.account.views import *
from django.urls import path, include
from django.contrib import admin


router = DefaultRouter()

router.register('web_register', WebUserRegisterViewset, basename='web_register')
router.register('web_login', WebUserLogin, basename='web_login')

router.register('refresh_token', RefreshTokenViewset, basename='refresh_token')

router.register('sent_otp_for_forgot_password', SentOTPForgetPassword, basename='sent_otp_for_forgot_password') 
router.register('forgot_password', ForgetPassword, basename='forgot_password') 
router.register('profile', UserProfile, basename='profile') 
router.register('profile_web', ProfileWeb, basename='profile_web') 

urlpatterns = [
    path('', include(router.urls)),
    path('change_password_confirmation/<str:token>', ChangePasswordConfirmationGenerics.as_view(),name='change_password_confirmation'),
    path('change_password_confirmation', ChangePasswordConfirmationGenerics.as_view(),name='change_password_confirmation')
]


