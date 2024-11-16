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
from rest_framework.permissions import AllowAny, IsAuthenticated

from api.v1.account.serializer import *
from api.v1.account.thread import SentOTPViaEmailThread
from api.v1.account.utils import *
from api.v1.models import *
from nexblooms.api_response import *
from nexblooms.messages import *

class WebUserRegisterViewset(ModelViewSet):
    """
    ViewSet for handling Web User Registration.
    """
    serializer_class = TempWebUserRegisterSerializer
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
        #     return http_500_response(error=str(e))



class WebUserLogin(ModelViewSet):
    http_method_names = ['post']
    serializer_class =WebUserLoginSerializer
    def get_queryset(self):
        return UserMaster.objects.all()
    
    def create(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            serializer = WebUserLoginSerializer(data=request.data)
            if serializer.is_valid():       
                user=UserMaster.objects.filter(email=email).last()
                remember_me = request.data.get('remember_me',None)
                serializer_data = WebUserDetailsSerialzier(user,context={'remember_me':remember_me,'request':request}).data
                AppUserTokens.objects.create(user_id = user.id, token = serializer_data['access_token'])
                return http_200_response_app(message=USER_LOGIN,data=serializer_data)
            else:
                if list(serializer.errors.keys())[0] != "error":
                    return http_400_response_app(message=f"{list(serializer.errors.keys())[0]} : {serializer.errors[list(serializer.errors.keys())[0]][0]}")
                else:
                    return http_400_response_app(message=serializer.errors[list(serializer.errors.keys())[0]][0])
        except Exception as e:
            return http_500_response_app(error=str(e))

class ChangePasswordConfirmationGenerics(View):
    serializer_class = ChangePasswordConfirmationGenericsSerializer

    def get(self, request, token):
        expiry_status = decode_reset_password_access_token(token)
        try:
            obj = UserMaster.objects.filter(email=expiry_status[1],password = expiry_status[2]).last()
            if not obj:
                return HttpResponse('link expired.')
            if expiry_status[0] == True:
                return render(request,'api/v1/change.html', {'token':token})
        except:
            return HttpResponse('link expired.')
    
    def post(self,request):
        try:
            token = request.POST.get('token')
            password = request.POST.get('password')
            confirm_password = request.POST.get('con_password')
            expiry_status = decode_reset_password_access_token(token)
            try:
                if expiry_status[0] == True:
                    password_status = passwordValidate(password, confirm_password)
                    if password_status[0] == False:
                        messages.error(request, password_status[1])
                        return render(request,'api/v1/change.html', {'token':token})
 
                    if password != confirm_password:
                        messages.error(request, "Password and Confirm password must be the same.")
                        return render(request,'api/v1/change.html', {'token':token})
                    else:
                        obj = UserMaster.objects.filter(email=expiry_status[1],password = expiry_status[2]).last()
                        if obj:
                            obj.password=make_password(password)
                            obj.raw_password= password
                            obj.save()
                            messages.success(request, "Success.")
                            return render(request,'api/v1/success.html', {'token':token})
                        else:
                            return HttpResponse('link expired.etrryt')
            except:
                return HttpResponse('link expired.')
        except Exception as e:
            return http_500_response_app(error=str(e))

# # Forget Password View
class SentOTPForgetPassword(ModelViewSet):
    serializer_class = SentOTPForgetPasswordSerializer

    http_method_names = ["post"]  
    def get_queryset(self):
        return UserMaster.objects.all()
    
    def create(self, request, *args, **kwargs):
        try:
            email = request.data.get('email',None)
            mobile_number = request.data.get('mobile_number',None)

            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                if email :
                    otp = generate_otp_for_email()
                    UserMaster.objects.filter(email=email).update(email_otp=otp, email_otp_generate_time=datetime.datetime.now())
                    record_data = {'email':email, 'otp':otp, 'first_name':f"{UserMaster.objects.filter(email=email).last().first_name}", 'last_name':f"{UserMaster.objects.filter(email=email).last().last_name}"}
                    SentOTPViaEmailThread(record_data).start()
                    return http_200_response(message=SEND_OTP,data=record_data)
                
                else:
                    return http_200_response(message=SEND_OTP)
            else:
                if list(serializer.errors.keys())[0] != "error":
                    return http_400_response(message=f"{list(serializer.errors.keys())[0]} : {serializer.errors[list(serializer.errors.keys())[0]][0]}")
                else:
                    return http_400_response(message=serializer.errors[list(serializer.errors.keys())[0]][0])
        except Exception as e:
            return http_500_response(error=str(e))


        
class ForgetPassword(ModelViewSet):
    serializer_class = ForgetPasswordSerializer

    http_method_names = ["post"]  
    def get_queryset(self):
        return UserMaster.objects.all()
    
    def create(self, request, *args, **kwargs):
        try:
            
            email = request.data.get('email')
            password = request.data.get('password')
            mobile_number = request.data.get('mobile_number')
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                if email:
                    user = UserMaster.objects.filter(email=email).last()
                    user.password = make_password(password)
                    user.raw_password = password
                    user.save()

                if mobile_number:
                    user = UserMaster.objects.filter(mobile_number=mobile_number).last()
                    user.password = make_password(password)
                    user.raw_password = password
                    user.save()
                
                return http_200_response(message=FORGET_PASSWORD)
            else:
                if list(serializer.errors.keys())[0] != "error":
                    return http_400_response(message=f"{list(serializer.errors.keys())[0]} : {serializer.errors[list(serializer.errors.keys())[0]][0]}")
                else:
                    return http_400_response(message=serializer.errors[list(serializer.errors.keys())[0]][0])
        
        except Exception as e:
            return http_500_response(error=str(e))



class UserProfile(ModelViewSet):
    http_method_names = ['get']
    # permission_classes = (permissions.IsAuthenticated,)
    queryset = UserMaster.objects.last()

    user_id = openapi.Parameter('user_id',in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)
    @swagger_auto_schema(manual_parameters=[user_id])
    def list(self,request):
        user_id= request.query_params.get("user_id")
        print(user_id,"IIIIIIIIIIIIIIIIIIIIIIIIIIIIDESBHVGDGD")
        queryset = UserMaster.objects.filter(id = user_id).values('id','first_name','last_name','full_name','mobile_number','email','address','image','is_active',"role__role","bio")
        dataframe = pd.DataFrame(queryset)
        # dataframe = dataframe.rename(columns={'role__role':'role',})
        base_url = request.build_absolute_uri('/')[:-1]+str('/media/')
        dataframe['image'] = dataframe['image'].apply(lambda x: base_url + x if x else '')
        data=dataframe.to_dict(orient="records")
        return http_200_response(message="Data found",data=data)




class RefreshTokenViewset(ModelViewSet):
    serializer_class= RefreshTokenSerializer
    http_method_names=['post']
    def create(self, request):
        try:
            serializer = RefreshTokenSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    payload = jwt.decode(request.data.get('access_token'), settings.SECRET_KEY, algorithms=["HS256"])
                except jwt.ExpiredSignatureError as e:
                    raise serializers.ValidationError({'error': 'Expired access token, please login again.'})
                user = UserMaster.objects.filter(id=payload.get('user_id')).first()
                serialized_user = SingleUserDetailsSerializer(user,context={'remember_me':True,"request":request}).data
                return http_200_response(message=USER_LOGIN,data =serialized_user)
                    # return http_201_response(message=TOKEN_REFRESH)        
            if list(serializer.errors.keys())[0] != "error":
                return http_400_response(message=f"{list(serializer.errors.keys())[0]} : {serializer.errors[list(serializer.errors.keys())[0]][0]}")
            else:
                return http_400_response(message=serializer.errors[list(serializer.errors.keys())[0]][0])
        except Exception as e:
            return http_500_response(error=str(e))


class ProfileWeb(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileWEBUpdateSerializer
    http_method_names = ['get','put']
    parser_classes = [parsers.FormParser, parsers.MultiPartParser]
    queryset = UserMaster.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'update':
            return ProfileWEBUpdateSerializer
        
        
    def list(self,request,*args, **kwargs):
        # try:
            data = request.user
            user_data = UserMaster.objects.filter(id = data.id).values()
            if user_data:
                df =pd.DataFrame(user_data)
                columns_to_drop = [
                    "password", "last_login", "role_id",
                    "mobile_otp", "email_otp", "mobile_otp_generate_time",
                    "email_otp_generate_time", "country", "countrymaster_id",
                    "raw_password", "is_password_changed",
                    "is_access_updated", "registered_by_id", "is_approved",
                    "created_by", "is_deleted", "updated_on" ,"fcm_token"
                ]
            
                df.drop(columns=columns_to_drop, inplace=True, errors='ignore')
                jason_data = df.to_json(orient='records')
                parsed_data = json.loads(jason_data) 
                return http_200_response(message=FOUND,data=parsed_data) 
            else:
                return http_200_response(message=NOT_FOUND)
        # except Exception as e:
        #     return http_500_response(error=str(e))
        
    def update(self, request, *args, **kwargs):
        # try:
            data_instance = UserMaster.objects.filter(id=(request.user.id)).last()
            serialized_data = ProfileWEBUpdateSerializer(data_instance,request.data,context={'user':request.user})
            if serialized_data.is_valid():
                data_obj=serialized_data.validated_data.get('id')
                show_data=ShowProfileWEBUpdateSerializer(data_obj,many=False,context={'request':request})

                return http_200_response(message=PROFILE_UPDATE,data=show_data.data)
            else:
                if list(serialized_data.errors.keys())[0] != "error":
                    return http_400_response(message=f"{list(serialized_data.errors.keys())[0]} : {serialized_data.errors[list(serialized_data.errors.keys())[0]][0]}")
                else:
                    return http_400_response(message=serialized_data.errors[list(serialized_data.errors.keys())[0]][0])
        # except Exception as e:
        #     return http_500_response(error=str(e))
        

