from django.views.generic import View
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status, permissions, filters, parsers
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.contrib import messages
from django.template.loader import render_to_string
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import django_filters.rest_framework
import pandas as pd
import numpy as np
import json
import datetime
import base64

from api.v1.account.serializer import AdminLoginSerializer, LoginUserDetailSerializer, UserLoginSerializer, WebUserRegisterSerializer
from api.v1.account.thread import SentOTPViaEmailThread
from api.v1.account.utils import *
from api.v1.models import UserMaster
from nexblooms.api_response import http_200_response, http_400_response, http_500_response
from nexblooms.messages import USER_CREATED
from rest_framework import generics, status, permissions

class WebUserRegisterViewset(ModelViewSet):
    """
    ViewSet for handling Web User Registration.
    """
    serializer_class = WebUserRegisterSerializer
    http_method_names = ["post"]

    def get_queryset(self):
        """
        Retrieves the queryset of all user records.

        Returns:
        - Queryset of all UserMaster objects.
        """
        return UserMaster.objects.all()

    def create(self, request, *args, **kwargs):
        """
        Handles the creation of a new web user.

        Parameters:
        - request: The HTTP request containing user data.

        Returns:
        - HTTP response with the status of the operation.
        """
        # try:
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # Get the last user with the provided email
            data = UserMaster.objects.filter(email=serializer.data['email']).last()
            if data:
                record_data = {
                    'email': data.email, 
                    'otp': data.email_otp, 
                    'first_name': data.first_name,
                    'last_name': data.last_name
                }
                user_data = {
                    'email': data.email, 
                    'otp': data.email_otp,
                    'mobile_otp': data.mobile_otp,
                    'mobile_number': data.mobile_number, 
                    'first_name': data.first_name,
                    'last_name': data.last_name
                }

                # Send OTP via email in a separate thread
                SentOTPViaEmailThread(record_data).start()

                return http_200_response(message=USER_CREATED, data=user_data)
            else:
                return http_400_response(message="User data not found.")
        else:
            # Handle validation errors
            error_key = list(serializer.errors.keys())[0]
            error_message = serializer.errors[error_key][0]
            if error_key != "error":
                return http_400_response(message=f"{error_key} : {error_message}")
            else:
                return http_400_response(message=error_message)
        # except Exception as e:
        #     # Handle unexpected exceptions
        #     return http_500_response(error=str(e))

    
    
class UserMobileLoginGenerics(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserLoginSerializer
    def post(self, request, *args, **kwargs):
        try:
        
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                user = UserMaster.objects.filter(email=request.data.get('email'),is_deleted=False).last()
                serialized_user = LoginUserDetailSerializer(user, many=False)
                print(serialized_user.data)
                context = {'status': True,'message': 'Login Successfully','data': serialized_user.data}
                return Response(context, status=status.HTTP_200_OK)
                
            context = {'status': False,'message': serializer.errors}
            return Response(context, status=status.HTTP_200_OK)
        except Exception as e:
            context = {'status': False, 'message': {"error": str(e)}}
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class AdminLogInViewset(ModelViewSet):
#     serializer_class = AdminLoginSerializer

#     http_method_names = ["post"]
#     def get_queryset(self):
#         return UserMaster.objects.all()
    
#     def create(self, request, *args, **kwargs):
#         email = request.data.get('email')
#         serializer = AdminLoginSerializer(data=request.data)
#         if serializer.is_valid():       
#             user=UserMaster.objects.filter(Q(email=email)|Q(username=email)).last()
#             remember_me = request.data.get('remember_me',None)
#             user.is_access_updated=False
#             user.save()
#             serializer_data = AdminDetailsSerializer(user,context={'remember_me':remember_me,'request':request}).data
#             return http_200_response(message=USER_LOGIN,data=serializer_data)
#         else:
#             if list(serializer.errors.keys())[0] != "error":
#                 return http_400_response(message=f"{list(serializer.errors.keys())[0]} : {serializer.errors[list(serializer.errors.keys())[0]][0]}")
#             else:
#                 return http_400_response(message=serializer.errors[list(serializer.errors.keys())[0]][0])
            
# class RefreshTokenViewset(ModelViewSet):
#     serializer_class= RefreshTokenSerializer
#     http_method_names=['post']
#     def create(self, request):
#         try:
#             serializer = RefreshTokenSerializer(data=request.data)
#             if serializer.is_valid():
#                 try:
#                     payload = jwt.decode(request.data.get('access_token'), settings.SECRET_KEY, algorithms=["HS256"])
#                 except jwt.ExpiredSignatureError as e:
#                     raise serializers.ValidationError({'error': 'Expired access token, please login again.'})
#                 user = UserMaster.objects.filter(id=payload.get('user_id')).first()
#                 serialized_user = SingleUserDetailsSerializer(user,context={'remember_me':True,"request":request}).data
#                 return http_200_response(message=USER_LOGIN,data =serialized_user)
#             if list(serializer.errors.keys())[0] != "error":
#                 return http_400_response(message=f"{list(serializer.errors.keys())[0]} : {serializer.errors[list(serializer.errors.keys())[0]][0]}")
#             else:
#                 return http_400_response(message=serializer.errors[list(serializer.errors.keys())[0]][0])
#         except Exception as e:
#             return http_500_response(error=str(e))
        

# class AdminForgetPasswordViewset(ModelViewSet):
#     serializer_class = ForgetPasswordSerializer
#     http_method_names = ["post"]
#     def create(self, request):
#         try:
#             email = request.data.get('email')
#             user = UserMaster.objects.filter(email=email).last()
#             if user:
#                 expt = datetime.datetime.now()
#                 uid = user.email
#                 subject= "Forgot Password"
#                 link = "api/v1/reset_password.html"
#                 recipient_list = [email,'mortalp369@gmail.com']
#                 cc_email= recipient_list
#                 token = reset_password_access_token(user)
#                 link_change_password = f"{request.scheme}://" +request.get_host()+ "/v1/account/change_password_confirmation/"+str(token)
#                 html_message = render_to_string(link, {'some_params': link_change_password})
#                 forget_password_mail(subject,recipient_list,cc_email,html_message)          
#                 return http_200_response(message=FORGOT_PASSWORD_MESSAGE,data=link_change_password)    
#             else:
#                 return http_400_response(message="User not exists")
#         except Exception as e:
#             return http_500_response(error=str(e))

# # Reset password
# class ChangePasswordConfirmationGenerics(View):
#     serializer_class = ChangePasswordConfirmationGenericsSerializer

#     def get(self, request, token):
#         expiry_status = decode_reset_password_access_token(token)
#         try:
#             obj = UserMaster.objects.filter(email=expiry_status[1],password = expiry_status[2]).last()
#             if not obj:
#                 return HttpResponse('link expired.')
#             if expiry_status[0] == True:
#                 return render(request,'api/v1/change.html', {'token':token})
                
#         except:
#             return HttpResponse('link expired.')
    
#     def post(self,request):
#         try:
#             token = request.POST.get('token')
#             password = request.POST.get('password')
#             confirm_password = request.POST.get('con_password')
#             expiry_status = decode_reset_password_access_token(token)
#             try:
#                 if expiry_status[0] == True:
#                     password_status = passwordValidate(password, confirm_password)
#                     if password_status[0] == False:
#                         messages.error(request, password_status[1])
#                         return render(request,'api/v1/change.html', {'token':token})
 
#                     if password != confirm_password:
#                         messages.error(request, "Password and Confirm password must be the same.")
#                         return render(request,'api/v1/change.html', {'token':token})
#                     else:
#                         obj = UserMaster.objects.filter(email=expiry_status[1],password = expiry_status[2]).last()
#                         if obj:
#                             obj.password=make_password(password)
#                             obj.raw_password= password
#                             obj.save()
#                             messages.success(request, "Success.")
#                             return render(request,'api/v1/success.html', {'token':token})
#                         else:
#                             return HttpResponse('link expired.etrryt')
#             except:
#                 return HttpResponse('link expired.')
#         except Exception as e:
#             return http_500_response(error=str(e))


# class WebUserLogin(ModelViewSet):
#     http_method_names = ['post']
#     serializer_class =WebUserLoginSerializer
#     def get_queryset(self):
#         return UserMaster.objects.all()
    
#     def create(self, request, *args, **kwargs):
#         try:
#             email = request.data.get('email')
#             serializer = WebUserLoginSerializer(data=request.data)
#             if serializer.is_valid():       
#                 user=UserMaster.objects.filter(email=email).last()
#                 remember_me = request.data.get('remember_me',None)
#                 serializer_data = WebUserDetailsSerialzier(user,context={'remember_me':remember_me,'request':request}).data
#                 AppUserTokens.objects.create(user_id = user.id, token = serializer_data['access_token'])
#                 user=UserMaster.objects.filter(email=email).update(fcm_token = request.data.get('fcm_token',None))
#                 return http_200_response_app(message=USER_LOGIN,data=serializer_data)
#             else:
#                 if list(serializer.errors.keys())[0] != "error":
#                     return http_400_response_app(message=f"{list(serializer.errors.keys())[0]} : {serializer.errors[list(serializer.errors.keys())[0]][0]}")
#                 else:
#                     return http_400_response_app(message=serializer.errors[list(serializer.errors.keys())[0]][0])
#         except Exception as e:
#             return http_500_response_app(error=str(e))

# class ChangePassword(ModelViewSet):
#     serializer_class = ChangePasswordSerializer
#     permission_classes = (permissions.IsAuthenticated,)

#     http_method_names = ["post"]  
#     def get_queryset(self):
#         return UserMaster.objects.all()

#     def create(self,request):
#         try:
#             serializer = ChangePasswordSerializer(data=request.data,context={"userid":request.user.id})
#             if serializer.is_valid():
#                 return http_201_response(message=CHANGE_PASSWORD)        
#             if list(serializer.errors.keys())[0] != "error":
#                 return http_400_response(message=f"{list(serializer.errors.keys())[0]} : {serializer.errors[list(serializer.errors.keys())[0]][0]}")
#             else:
#                 return http_400_response(message=serializer.errors[list(serializer.errors.keys())[0]][0])
#         except Exception as e:
#             return http_500_response(error=str(e))

        


# # Forget Password View
# class SentOTPForgetPassword(ModelViewSet):
#     serializer_class = SentOTPForgetPasswordSerializer

#     http_method_names = ["post"]  
#     def get_queryset(self):
#         return UserMaster.objects.all()
    
#     def create(self, request, *args, **kwargs):
#         try:
            
#             email = request.data.get('email',None)
#             mobile_number = request.data.get('mobile_number',None)
#             country = request.data.get('country',None)
#             print(mobile_number,'ggggggggggg',country)
            
#             serializer = self.serializer_class(data=request.data)
#             if serializer.is_valid():
#                 # if mobile_number is None:
#                 if email and (not mobile_number):
#                     otp = generate_otp_for_email()
#                     UserMaster.objects.filter(email=email).update(email_otp=otp, email_otp_generate_time=datetime.datetime.now())
#                     record_data = {'email':email, 'otp':otp, 'first_name':f"{UserMaster.objects.filter(email=email).last().first_name}", 'last_name':f"{UserMaster.objects.filter(email=email).last().last_name}"}
#                     SentOTPViaEmailThread(record_data).start()
#                     return http_200_response(message=SEND_OTP,data=record_data)
#                 # if email is None:
#                 if (mobile_number) and (not email ):
#                         user_check = UserMaster.objects.filter(mobile_number=mobile_number).last()
#                         if user_check :
#                             otp = generate_otp_for_mobile()
#                             UserMaster.objects.filter(mobile_number=mobile_number).update(mobile_otp=otp,mobile_otp_generate_time=datetime.datetime.now())
#                             record_data = {'mobile_number':mobile_number, 'otp':otp, 'first_name':f"{UserMaster.objects.filter(mobile_number=mobile_number).last().first_name}", 'last_name':f"{UserMaster.objects.filter(mobile_number=mobile_number).last().last_name}"}
#                             return http_200_response(message=SEND_OTP_SUCCESS,data=record_data)
#                         else:
#                             return http_400_response(message=SEND_OTP_MOBILE)
#                 else:
#                     return http_200_response(message=SEND_OTP)
#             else:
#                 if list(serializer.errors.keys())[0] != "error":
#                     return http_400_response(message=f"{list(serializer.errors.keys())[0]} : {serializer.errors[list(serializer.errors.keys())[0]][0]}")
#                 else:
#                     return http_400_response(message=serializer.errors[list(serializer.errors.keys())[0]][0])
#         except Exception as e:
#             return http_500_response(error=str(e))


        
# class ForgetPassword(ModelViewSet):
#     serializer_class = ForgetPasswordSerializer

#     http_method_names = ["post"]  
#     def get_queryset(self):
#         return UserMaster.objects.all()
    
#     def create(self, request, *args, **kwargs):
#         try:
            
#             email = request.data.get('email')
#             password = request.data.get('password')
#             mobile_number = request.data.get('mobile_number')
#             serializer = self.serializer_class(data=request.data)
#             if serializer.is_valid():
#                 if email:
#                     user = UserMaster.objects.filter(email=email).last()
#                     user.password = make_password(password)
#                     user.raw_password = password
#                     user.save()

#                 if mobile_number:
#                     user = UserMaster.objects.filter(mobile_number=mobile_number).last()
#                     user.password = make_password(password)
#                     user.raw_password = password
#                     user.save()
                
#                 return http_200_response(message=FORGET_PASSWORD)
#             else:
#                 if list(serializer.errors.keys())[0] != "error":
#                     return http_400_response(message=f"{list(serializer.errors.keys())[0]} : {serializer.errors[list(serializer.errors.keys())[0]][0]}")
#                 else:
#                     return http_400_response(message=serializer.errors[list(serializer.errors.keys())[0]][0])
        
#         except Exception as e:
#             return http_500_response(error=str(e))



# class UseRProfile(ModelViewSet):
#     http_method_names = ['get']
#     # permission_classes = (permissions.IsAuthenticated,)
#     queryset = UserMaster.objects.last()

#     user_id = openapi.Parameter('user_id',in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)
#     @swagger_auto_schema(manual_parameters=[user_id])
#     def list(self,request):
#         user_id= request.query_params.get("user_id")
#         queryset = UserMaster.objects.filter(id = user_id).values('id','first_name','last_name','full_name','mobile_number',"licence",'email','address','image','is_active',"role__role","country","bio")
#         dataframe = pd.DataFrame(queryset)
#         # dataframe['licence_id'] = "DL14 20110012345"
#         dataframe['licence'] = dataframe['licence'].fillna("")
#         dataframe.rename(columns={"licence":"licence_id",'role__role':'role'},inplace=True)
#         # dataframe = dataframe.rename(columns={'role__role':'role',})
#         base_url = request.build_absolute_uri('/')[:-1]+str('/media/')
#         dataframe['image'] = dataframe['image'].apply(lambda x: base_url + x if x else '')
#         data=dataframe.to_dict(orient="records")
#         return http_200_response(message="Data found",data=data)
    
