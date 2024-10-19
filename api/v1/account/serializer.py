import re
import random
import string
import datetime
from django.db import transaction
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from rest_framework import serializers
from api.v1.account.utils import generate_otp_for_mobile, generate_otp_for_email
from api.v1.models import UserMaster

# *************************************
# Regular Expressions
# *************************************

# Email Regular Expression
EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

# Mobile Number Regular Expression
MOBILE_PATTERN = re.compile(r"^\+?[1-9][0-9]{7,14}$")

# *************************************
# Utility Functions
# *************************************

def generate_password(length=10):
    """
    Generates a random password with the given length.

    Parameters:
    - length: Length of the password (default is 10).

    Returns:
    - A string representing the generated password.
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

# *************************************
# Web User Registration Serializer
# *************************************

class WebUserRegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        required=True,
        error_messages={'invalid': 'Please enter a valid first name.'}
    )
    last_name = serializers.CharField(
        required=True,
        error_messages={'invalid': 'Please enter a valid last name.'}
    )
    email = serializers.CharField(
        required=True,
        error_messages={'invalid': 'Please enter a valid email.'}
    )
    mobile_number = serializers.CharField(
        required=True,
        error_messages={'invalid': 'Please enter a valid mobile number.'}
    )
    country = serializers.CharField(
        required=True,
        error_messages={'invalid': 'Please enter a valid country code.'}
    )
    password = serializers.CharField(
        required=True,
        error_messages={'invalid': 'Please enter the password.'}
    )
    confirm_password = serializers.CharField(
        required=True,
        error_messages={'invalid': 'Please enter the confirm password.'}
    )

    class Meta:
        model = UserMaster
        fields = ['id', 'first_name', 'last_name', 'email', 'mobile_number', 'country', 'password', 'confirm_password']

    def validate(self, attrs):
        """
        Validates the provided data for user registration.

        Parameters:
        - attrs: Dictionary of user attributes.

        Returns:
        - The validated attributes.
        """
        first_name = attrs.get('first_name')
        last_name = attrs.get('last_name')
        email = attrs.get('email')
        mobile_number = attrs.get('mobile_number')
        country = attrs.get('country')
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')


        # Validate password match
        if password != confirm_password:
            raise serializers.ValidationError({'error': 'Password does not match.'})

        # Validate first name and last name
        if not (first_name or last_name):
            raise serializers.ValidationError({'error': 'Please provide first name or last name.'})

        # Validate email
        if email:
            if UserMaster.objects.filter(email=email).exists():
                raise serializers.ValidationError({'error': 'User with this email already exists.'})
            if not re.fullmatch(EMAIL_REGEX, email):
                raise serializers.ValidationError({'error': 'Please enter a valid email.'})
        else:
            raise serializers.ValidationError({'error': 'Please provide email.'})

        # Validate mobile number
        if mobile_number:
            if UserMaster.objects.filter(mobile_number=mobile_number).exists():
                raise serializers.ValidationError({'error': 'User with this mobile number already exists.'})
            if not MOBILE_PATTERN.match(mobile_number):
                raise serializers.ValidationError({'error': 'Please enter a valid mobile number.'})
        else:
            raise serializers.ValidationError({'error': 'Please provide mobile number.'})

        # Validate country
        if not country:
            raise serializers.ValidationError({'error': 'Please provide country.'})

        # Create and save the new user
        with transaction.atomic():
            user = UserMaster(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=email,
                mobile_number=mobile_number,
                country=country,
                password=make_password(password),
                raw_password=password,
                is_active=True,
                role_id=int(3),

                mobile_otp=generate_otp_for_mobile(),
                email_otp=generate_otp_for_email(),
                mobile_otp_generate_time=datetime.datetime.now(),
                email_otp_generate_time=datetime.datetime.now()
            )
            user.save()

        return attrs


from curses.ascii import isdigit
import datetime
from email.policy import default

import re

from urllib import request

from django.conf import settings
from pkg_resources import require
from rest_framework import serializers
from api.v1.account.utils import generate_access_token, generate_refresh_token
from django.contrib.auth import get_user_model
from api.v1.models import *


User = get_user_model()

### User Login Serializer.
class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=100,error_messages={'blank': 'Please enter user id'})
    password = serializers.CharField(max_length=128,error_messages={'blank': 'Please enter password'})
    class Meta:
        ref_name = 'UserLoginMobile'
        model = User
        fields = ('email','password')

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        user = User.objects.filter(email=email,is_deleted=False).last()
        if user is None:
            raise serializers.ValidationError({'error' : 'Please enter correct User Id.'})
        if (not user.check_password(password)):
            raise serializers.ValidationError({'error' : 'User Id or Password incorrect.Please try again.'})

        ## Check role only login FA and DM.
        # if user.roles_id in [1,2,5,6]:  ## check user roles
        #     raise serializers.ValidationError({'error' : 'Only login FA or DM.Please try again.'})
        if user.is_active == False:
            raise serializers.ValidationError({'error' : 'Your account is inactive.Please contact support team.'})
            
        return super().validate(attrs)


class LoginUserDetailSerializer(serializers.ModelSerializer):
    access_token = serializers.SerializerMethodField()
    refresh_token = serializers.SerializerMethodField()
    
    class Meta:
        ref_name = 'SingleUserMobilDetail'
        model = User
        fields = ('id','email','first_name','last_name','username','role','access_token','refresh_token')
    def get_access_token(self, obj):
        return generate_access_token(obj.id)
    def get_refresh_token(self, obj):
        return generate_refresh_token(obj.id)
    

class AdminLoginSerializer(serializers.ModelSerializer):
    email= serializers.CharField(max_length=100)
    password= serializers.CharField(max_length=100)
    remember_me= serializers.BooleanField(default=True)
    

    class Meta:
        model = UserMaster
        fields = ['email', 'password',"remember_me"]

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user_check = UserMaster.objects.filter(Q(email=email)|Q(username = email),is_deleted=False).exclude(is_approved="rejected").last()
        if not user_check:
            raise serializers.ValidationError({'error':'Entered email does not exists.'})

        user_role_check = UserMaster.objects.filter(Q(email=email)|Q(username=email),is_deleted=False).exclude(is_approved="rejected").last().role_id
        if not user_role_check==3:
            if not user_check.is_active:
                raise serializers.ValidationError({'error':'Your Account is inactive.'})
        
        if not (user_role_check in [1,2]):
            raise serializers.ValidationError({'error':'You are not allowed to login.'})
        
        if not (user_check.check_password(password)):
            raise serializers.ValidationError({'error':'You have entered wrong password.'})
        
       

        return attrs
# class RefreshTokenSerializer(serializers.ModelSerializer):
#     access_token = serializers.CharField(required=True,error_messages={'blank': 'Please enter access_token'})
#     class Meta:
#         model = UserMaster
#         fields=['access_token']
#     def validate(self, attrs):
#         access_token = attrs.get('access_token')
#         try:
#             payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
#         except jwt.ExpiredSignatureError as e:
#             raise serializers.ValidationError({'error': 'Expired access token, please login again.'})
#         user = UserMaster.objects.filter(id=payload.get('user_id')).first()
#         if user is None:
#             raise serializers.ValidationError({'error' : 'User not found'})
#         if not user.is_active:
#             raise serializers.ValidationError({'error' : 'User is inactive'})
#         return attrs
# class AdminDetailsSerializer(serializers.ModelSerializer):
#     access_token = serializers.SerializerMethodField()
#     refresh_token = serializers.SerializerMethodField()
#     role = serializers.SerializerMethodField()
#     country = serializers.SerializerMethodField()
#     role_id  = serializers.SerializerMethodField()
#     iscommission_set_by_admin = serializers.SerializerMethodField()
#     commission = serializers.SerializerMethodField()
#     ismembership_purchased = serializers.SerializerMethodField()
#     profile_image = serializers.SerializerMethodField()
    
#     class Meta:
#         model = UserMaster
#         fields = ['id','first_name','last_name','full_name','email','mobile_number',"created_by",'username','role_id',
#                     'role','iscommission_set_by_admin',"commission","ismembership_purchased",'country','is_active','is_email_verified','is_mobile_verified',"is_approved",
#                     'access_token','refresh_token','profile_image','is_password_changed']
#     def get_role_id(self,obj):
#         return obj.role_id
#     def get_role(self,obj):
#         return obj.role.role
#     def get_country(self,obj):
#         return obj.country
#     def get_iscommission_set_by_admin(self,obj):
#         try:
#             vendor = VendorMaster.objects.filter(user_id = obj.id).last()
#             return vendor.iscommission_set_by_admin
#         except:
#             return ""   
#     def get_access_token(self, obj): 
#         remember_me = self.context.get('remember_me')
#         return get_access_tokens_for_user(obj.id,remember_me)

#     def get_refresh_token(self, obj):
#         remember_me = self.context.get('remember_me')
        
#         return get_refres_tokens_for_user(obj.id,remember_me)
#     def get_commission(self, obj):
#         try:
#             vendor = VendorMaster.objects.filter(user_id = obj.id).last()
#             return vendor.commission
#         except:
#             return ""
#     def get_ismembership_purchased(self, obj):
#         try:
#             vendor = VendorMembershipMapping.objects.filter(user_id = obj.id).last()
#             if vendor:
#                 return True
#             else:
#                 return False
#         except:
#             return ""
#     def get_profile_image(self,obj):
#         try:
#             request = self.context.get('request')
#             base_url = request.build_absolute_uri('/')[:-1]+str('/media/')
#             if obj.role.id !=3:
#                 if obj.image:
#                     image_obj=(str(base_url) + str(obj.image))
#                     return image_obj
#                 else:
#                     return ""
#             else:
#                 vendor = VendorMaster.objects.filter(user_id = obj.id).last()
#                 if vendor.logo:
#                     image_obj=(str(base_url) + str(vendor.logo))
#                     return image_obj
#                 else:
#                     return ""
#         except:
#             return ""   

#     # def get_roles_access(self, obj):
#     #     if obj.roles_id == 1:
#     #         return "ADMIN"
#     #     else:
#     #         user_roles = MapRolesAccessToSubAdmin.objects.filter(user_id=obj.id).values_list('roles_access')
#     #         roles = RoleAccessMaster.objects.filter(id__in=user_roles).all()
#     #         if roles:
#     #             serializer = AccessRolesSerializers(roles, many=True)
#     #             return serializer.data
#     #         return None


# class DummySerializer(serializers.Serializer):
#     name =serializers.CharField(max_length =100)
#     class Meta:
#         fields = ['name']
        
        


# class WebUserLoginSerializer(serializers.Serializer):
#     email= serializers.CharField(max_length=100)
#     password= serializers.CharField(max_length=100)
#     remember_me= serializers.BooleanField(default=True)
#     fcm_token= serializers.CharField(allow_null=True,allow_blank=True,default="")
#     class Meta:
#         model = UserMaster
#         fields = ['email', 'password',"remember_me","fcm_token"]

#     def validate(self, attrs):
#         email = attrs.get('email')
#         password = attrs.get('password')

#         user_check = UserMaster.objects.filter(Q(email=email)|Q(username = email),is_deleted=False).exclude(is_approved="rejected").last()
#         if not user_check:
#             raise serializers.ValidationError({'error':"The entered email doesn't exist"})
#         if not user_check.is_active:
#             raise serializers.ValidationError({'error':'Your Account is inactive.'})
        
#         user_role_check = UserMaster.objects.filter(Q(email=email)|Q(username=email),is_deleted=False).exclude(is_approved="rejected").last().role_id
#         if not (user_role_check in [4,5]):
#             raise serializers.ValidationError({'error':'You are not allowed to login.'})
        
#         if not (user_check.check_password(password)):
#             raise serializers.ValidationError({'error':'You have entered wrong password.'})
#         return attrs
# class WebUserDetailsSerialzier(serializers.ModelSerializer):
#     access_token = serializers.SerializerMethodField()
#     refresh_token = serializers.SerializerMethodField()
#     role = serializers.SerializerMethodField()
#     country = serializers.SerializerMethodField()
#     country_id = serializers.SerializerMethodField()
#     country_name = serializers.SerializerMethodField()
#     # roles_access = serializers.SerializerMethodField() 
#     image = serializers.SerializerMethodField()  
#     flag = serializers.SerializerMethodField()
#     currency_symbol = serializers.SerializerMethodField()  


#     class Meta:
#         model = UserMaster
#         fields = ['id','first_name','last_name','full_name','email','mobile_number','username','role','country','country_id','country_name','is_active','is_email_verified','is_mobile_verified','access_token','refresh_token','image','flag','currency_symbol']
    
#     def get_role(self,obj):
#         return obj.role.role
#     def get_flag(self,obj):
#         try:
#             request=self.context.get('request')
#             base_url = base_url = request.build_absolute_uri("/")
#             if obj.countrymaster.flag_image and obj.countrymaster.flag_image.url and base_url:
#                 flag_image_url = obj.countrymaster.flag_image.url
#                 return f"{base_url.strip('/')}{flag_image_url}"
#             else:
#                 return ""
#         except:
#             return ""
    
#     # def get_currency_symbol(self,obj):
#     #     if obj.countrymaster:
#     #         return obj.countrymaster.currency_symbol
#     #     else:
#     #         return ""
#     def get_currency_symbol(self,obj):
#         if obj.countrymaster:
#             return html.unescape(obj.countrymaster.currency_symbol)
#         else:
#             return ""
#     def get_country(self,obj):
#         if obj.countrymaster:
#             return obj.countrymaster.code
#         else:
#             return ""
#     def get_country_id(self,obj):
#         if obj.countrymaster:
#             return obj.countrymaster.id
#         else:
#             return None
#     def get_country_name(self,obj):
#         if obj.countrymaster:
#             return obj.countrymaster.name
#         else:
#             return ""
#     def get_access_token(self, obj): 
#         remember_me = self.context.get('remember_me')
#         return get_web_access_tokens_for_user(obj.id,remember_me)

#     def get_refresh_token(self, obj):
#         remember_me = self.context.get('remember_me')
#         return get_web_refresh_tokens_for_user(obj.id,remember_me)

#     def get_image(self,obj):
#         request = self.context.get('request')
#         base_url = request.build_absolute_uri('/')[:-1]+str('/media/')
#         try:
#             if obj.image and base_url:
#                 return str(base_url)+str(obj.image)
#             else:
#                 return ""
#         except:
#             return ""   
   
# class SingleUserDetailsSerializer(serializers.ModelSerializer):
#     access_token = serializers.SerializerMethodField()
#     refresh_token = serializers.SerializerMethodField()
#     role = serializers.SerializerMethodField()
 
    
    
#     class Meta:
#         model = UserMaster
#         fields = ['id','first_name','last_name','full_name','email','mobile_number','username','role','country','is_active','is_email_verified','is_mobile_verified','access_token','refresh_token']
    
    
#     def get_role(self,obj):
#         if obj.role.role:   
#             return obj.role.role
#         else:
#             return None
       
#     def get_access_token(self, obj): 
#         remember_me = self.context.get('remember_me')
#         return get_access_tokens_for_user(obj.id,remember_me)

#     def get_refresh_token(self, obj):
#         remember_me = self.context.get('remember_me')
        
#         return get_refres_tokens_for_user(obj.id,remember_me)
    
   
      
# # change password  Serializer
# class ChangePasswordSerializer(serializers.Serializer):
        
#         old_password = serializers.CharField(max_length = 30)
#         new_password = serializers.CharField(max_length = 30)
#         confirm_new_password = serializers.CharField(max_length = 30)
        
        
#         def validate(self, attrs):
            
#             if attrs.get('new_password') != attrs.get('confirm_new_password'):
#                 raise serializers.ValidationError({"error":"Passwords don't match."})
         
#             user = UserMaster.objects.filter(id=self.context.get('userid')).last()
#             check_pass = check_password(attrs.get('new_password'),user.password)
#             check_pass1 = check_password(attrs.get('old_password'),user.password)
#             if check_pass == True:
#                 raise serializers.ValidationError({"error":"you cannot use current password"})
#             if check_pass1 != True:
#                 raise serializers.ValidationError({"error":"Old Password is not correct."})
            
#             user = UserMaster.objects.filter(id=self.context.get('userid')).update(password = make_password(attrs.get('confirm_new_password')))
#             return super().validate(attrs)
  
# # Sent OTP for forgot Password
# class SentOTPForgetPasswordSerializer(serializers.Serializer):
#     email= serializers.CharField(max_length=100, required=False,allow_blank=True)
#     mobile_number= serializers.CharField(max_length=100,  required=False,allow_blank=True)
#     country= serializers.IntegerField( required=False)
    
    
#     class Meta:
#         # model = UserMaster
#         fields = ['mobile_number', 'email']

#     def validate(self, attrs):
#         email = attrs.get('email')
#         mobile_number = attrs.get('mobile_number')

#         if not email and not mobile_number:
#             raise serializers.ValidationError({'error':'Please provide email or mobile number.'})
        
#         # if email and mobile_number:
#         #     raise serializers.ValidationError({'error':'Please provide email or mobile number at a time.'})
        
#         if email:
#             if not UserMaster.objects.filter(email=email).exists():
#                 raise serializers.ValidationError({"error":'This email address is not registered with us.'})
#             if not UserMaster.objects.filter(email=email, is_active=True, is_deleted=False).exists():
#                 raise serializers.ValidationError({"error":'You are not allowed to login.'})
            
#         if mobile_number:
#             if not UserMaster.objects.filter(mobile_number=mobile_number).exists():
#                 raise serializers.ValidationError({"error":'This mobile number is not registered with us.'})
#             if not UserMaster.objects.filter(mobile_number=mobile_number, is_active=True, is_deleted=False).exists():
#                 raise serializers.ValidationError({"error":'You are not allowed to login.'})
        

#         return attrs

# class ForgetPasswordSerializer(serializers.Serializer):
#     email= serializers.CharField(max_length=100, required=False)
#     mobile_number= serializers.CharField(max_length=100, required=False)
#     otp = serializers.CharField(max_length=4, required=False)
#     password= serializers.CharField(max_length=100, required=False)
#     confirm_password= serializers.CharField(max_length=100, required=False)
    
#     class Meta:
#         # model = UserMaster
#         fields = ['mobile_number', 'email','password','confirm_password']

#     def validate(self, attrs):
#         email = attrs.get('email')
#         mobile_number = attrs.get('mobile_number')
#         otp = attrs.get('otp')
#         password = attrs.get('password')
#         confirm_password = attrs.get('confirm_password')

#         if not email and not mobile_number:
#             raise serializers.ValidationError({'error':'Please provide email or mobile number.'})
        
      
        
#         if email:
#             if not UserMaster.objects.filter(email=email).exists():
#                 raise serializers.ValidationError({"error":'This email address is not registered wiht us.'})
#             if not UserMaster.objects.filter(email=email, is_active=True, is_deleted=False).exists():
#                 raise serializers.ValidationError({"error":'You are not allowed to login.'})
#             if UserMaster.objects.filter(email=email, is_active=True, is_deleted=False).last().email_otp != otp:
#                 raise serializers.ValidationError({"error":'Entered otp is not correct..'})
            
#             time = otp_email_time_generate(UserMaster.objects.filter(email=email, is_active=True, is_deleted=False).last())
#             print(time, datetime.datetime.now())
            
#             if not (time >=0 and time <=10):
#                 raise serializers.ValidationError({"error":'Otp Is Expired, please generate again.'})


            
#         if mobile_number:
#             if not UserMaster.objects.filter(mobile_number=mobile_number).exists():
#                 raise serializers.ValidationError({"error":'This mobile number is not registered wiht us.'})
#             if not UserMaster.objects.filter(mobile_number=mobile_number, is_active=True, is_deleted=False).exists():
#                 raise serializers.ValidationError({"error":'You are not allowed to login.'})
#             if UserMaster.objects.filter(mobile_number=mobile_number, is_active=True, is_deleted=False).last().mobile_otp != otp:
#                 raise serializers.ValidationError({"error":'Entered otp is not correct..'})
#             time = otp_time_generate(UserMaster.objects.filter(mobile_number=mobile_number, is_active=True, is_deleted=False).last())
            
#             print(time, datetime.datetime.now())
#             if not (time >=0 and time <=10):
#                 raise serializers.ValidationError({"error":'Otp Is Expired, please generate again.'})

            
#         if not password and not confirm_password:
#             raise serializers.ValidationError({"error":'Password and confirm password is mandatory'})
        
#         if password != confirm_password:
#             raise serializers.ValidationError({"error":'Password and confirm password does not match.'})


#         return attrs

    

# class ForgetPasswordSerializer(serializers.Serializer):
#     email= serializers.CharField(max_length=100, required=False)
    
# class ChangePasswordConfirmationGenericsSerializer(serializers.Serializer):
#     password= serializers.CharField(max_length=100, required=False)
#     confirm_password= serializers.CharField(max_length=100, required=False)
    
#     class Meta:
#         # model = UserMaster
#         fields = ['password','confirm_password']
        
#     def validate(self, attrs):
#         password = attrs.get('password')
#         confirm_password = attrs.get('confirm_password')   

      
#         if not password and not confirm_password:
#             raise serializers.ValidationError({"error": 'Password and confirm password are mandatory'})

      
#         password_regex = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-+=/_]).{8,}$"

        
#         if not bool(re.fullmatch(password_regex, attrs['password'])):
#             raise serializers.ValidationError({'error': "Password must be 8 characters long, alphanumeric, and must contain special characters"})

   
#         if password != confirm_password:
#             raise serializers.ValidationError({"error": 'Password and confirm password do not match.'})

#         return attrs
    

# class DriverLoginSerializer(serializers.ModelSerializer):
#     email= serializers.CharField(max_length=100)
#     password= serializers.CharField(max_length=100)
#     remember_me= serializers.BooleanField(default=True)
    

#     class Meta:
#         model = UserMaster
#         fields = ['email', 'password',"remember_me"]

#     def validate(self, attrs):
#         email = attrs.get('email')
#         password = attrs.get('password')
#         user_check = UserMaster.objects.filter(Q(email=email)|Q(username = email),is_deleted=False).exclude(is_approved="rejected").last()
#         if not user_check:
#             raise serializers.ValidationError({'error':'Entered email does not exists.'})
#         if user_check.role_id != 6:
#             raise serializers.ValidationError({'error':'Invalid credentials.'})
#         user_role_check = UserMaster.objects.filter(Q(email=email)|Q(username=email),is_deleted=False).exclude(is_approved="rejected").last().role_id
#         if not user_role_check==6:
#             if not user_check.is_active:
#                 raise serializers.ValidationError({'error':'Your Account is inactive.'})
        
#         if not (user_check.check_password(password)):
#             raise serializers.ValidationError({'error':'You have entered wrong password.'})
        

#         return attrs
    

# class DriverDetailsSerializer(serializers.ModelSerializer):
#     access_token = serializers.SerializerMethodField()
#     refresh_token = serializers.SerializerMethodField()
#     role = serializers.SerializerMethodField()
#     country = serializers.SerializerMethodField()
#     role_id  = serializers.SerializerMethodField()
#     iscommission_set_by_admin = serializers.SerializerMethodField()
#     commission = serializers.SerializerMethodField()
#     ismembership_purchased = serializers.SerializerMethodField()
#     profile_image = serializers.SerializerMethodField()
    
#     class Meta:
#         model = UserMaster
#         fields = ['id','first_name','last_name','full_name','email','mobile_number',"created_by",'username','role_id',
#                     'role','iscommission_set_by_admin',"commission","ismembership_purchased",'country','is_active','is_email_verified','is_mobile_verified',"is_approved",
#                     'access_token','refresh_token','profile_image','is_password_changed']
#     def get_role_id(self,obj):
#         return obj.role_id
#     def get_role(self,obj):
#         return obj.role.role
#     def get_country(self,obj):
#         return obj.country
#     def get_iscommission_set_by_admin(self,obj):
#         try:
#             vendor = VendorMaster.objects.filter(user_id = obj.id).last()
#             return vendor.iscommission_set_by_admin
#         except:
#             return ""   
#     def get_access_token(self, obj): 
#         remember_me = self.context.get('remember_me')
#         return get_access_tokens_for_user(obj.id,remember_me)

#     def get_refresh_token(self, obj):
#         remember_me = self.context.get('remember_me')
        
#         return get_refres_tokens_for_user(obj.id,remember_me)
#     def get_commission(self, obj):
#         try:
#             vendor = VendorMaster.objects.filter(user_id = obj.id).last()
#             return vendor.commission
#         except:
#             return ""
#     def get_ismembership_purchased(self, obj):
#         try:
#             vendor = VendorMembershipMapping.objects.filter(user_id = obj.id).last()
#             if vendor:
#                 return True
#             else:
#                 return False
#         except:
#             return ""
#     def get_profile_image(self,obj):
#         try:
#             request = self.context.get('request')
#             base_url = request.build_absolute_uri('/')[:-1]+str('/media/')
#             if obj.role.id !=3:
#                 if obj.image:
#                     image_obj=(str(base_url) + str(obj.image))
#                     return image_obj
#                 else:
#                     return ""
#             else:
#                 vendor = VendorMaster.objects.filter(user_id = obj.id).last()
#                 if vendor.logo:
#                     image_obj=(str(base_url) + str(vendor.logo))
#                     return image_obj
#                 else:
#                     return ""
#         except:
#             return ""   

#     # def get_roles_access(self, obj):
#     #     if obj.roles_id == 1:
#     #         return "ADMIN"
#     #     else:
#     #         user_roles = MapRolesAccessToSubAdmin.objects.filter(user_id=obj.id).values_list('roles_access')
#     #         roles = RoleAccessMaster.objects.filter(id__in=user_roles).all()
#     #         if roles:
#     #             serializer = AccessRolesSerializers(roles, many=True)
#     #             return serializer.data
#     #         return None


# class DriverRegisterSerializer(serializers.ModelSerializer):
#     full_name = serializers.CharField(required = True,error_messages={'invalid': 'Please enter a valid full_name.'})
#     licence = serializers.CharField(required = True,error_messages={'invalid': 'Please enter a valid licence.'})
#     email = serializers.CharField(required = True,error_messages={'invalid': 'Please enter a valid email.'})
#     mobile_number=serializers.CharField(required = True,error_messages={'invalid': 'Please enter a valid mobile_number.'})
#     # password = serializers.CharField()
#     # confirm_password = serializers.CharField()
#     store_id = serializers.CharField(required = True,error_messages={'invalid': 'Please enter the store_id.'})
#     address = serializers.CharField()
#     username = serializers.CharField(allow_null=True,allow_blank=True,default="")
#     # created_by = serializers.CharField()
    
#     class Meta:
#         model = UserMaster
#         fields = ['id','full_name','licence', 'email', 'mobile_number',"store_id","address","username"]

#     def validate(self, attrs):
#         # try:
#             full_name = attrs.get('full_name')
#             licence = attrs.get('licence')
#             store_id = attrs.get('store_id')
#             email = attrs.get('email')
#             mobile_number = attrs.get('mobile_number')
#             # password = attrs.get('password')
#             # confirm_password = attrs.get('confirm_password')
#             address = attrs.get('address')
#             # created_by = attrs.get('created_by')
#             # Pattern = re.compile("(0|91)?[6-9][0-9]{9}")

#             # if not (int(role_id) in [6]):    
#             #     raise serializers.ValidationError({'error':'Please provide valid role id.'})
                    
            
#             # if password!=confirm_password:
#             #     raise serializers.ValidationError({'error':'Password does not match.'})
            
                
#             if not (full_name):
#                 raise serializers.ValidationError({'error':'Please provide first name or last name.'})
            
#             if email:
#                 if UserMaster.objects.filter(email=email).exists():
#                     raise serializers.ValidationError({'error':'User with this email already exists.'})
#                 if not re.fullmatch(email_regex, email):
#                     raise serializers.ValidationError({'error':'Please enter a valid email.'})                
#             else:
#                 raise serializers.ValidationError({'error':'Please provide email.'})
            
#             if mobile_number:
#                 if UserMaster.objects.filter(mobile_number=mobile_number).exists():
#                     raise serializers.ValidationError({'error':'User with this Phone number already exists.'})
#                 # if not Pattern.match(mobile_number):
#                 #     raise serializers.ValidationError({'error':'Please enter a valid mobile number.'})
#             else:
#                 raise serializers.ValidationError({'error':'Please provide phone number.'})
            
#             # name=full_name.split(" ")
#             name=full_name

#             # pass_gen = generate_password(10)
#             pass_gen = "Password@123"
#             obj = UserMaster()
#             with transaction.atomic():
#                 obj.first_name=full_name
#                 obj.last_name=full_name
#                 obj.full_name=full_name
#                 obj.email=email
#                 obj.username=email
#                 obj.mobile_number=mobile_number
#                 obj.role_id = 6
#                 obj.password= make_password(pass_gen)
#                 obj.raw_password= pass_gen
#                 obj.is_active=True
#                 obj.registered_by_id=self.context.get("userid")
#                 obj.address=address
#                 obj.mobile_otp = generate_otp_for_mobile()
#                 obj.email_otp = generate_otp_for_email()
#                 obj.mobile_otp_generate_time = datetime.datetime.now()
#                 obj.email_otp_generate_time = datetime.datetime.now()     
#                 obj.licence = licence
#                 obj.save()

#             obj_driver = DriverVendorMapping()
#             with transaction.atomic():
#                 obj_driver.driver_id = obj.id
#                 obj_driver.vendor_id = self.context.get("userid")
#                 obj_driver.store_id = store_id
#                 obj_driver.save()
#             return attrs
        
        
# class DriverUpdateSerializer(serializers.ModelSerializer):
#     full_name = serializers.CharField(allow_null=True,allow_blank=True)
#     licence = serializers.CharField(allow_null=True,allow_blank=True)
#     mobile_number=serializers.CharField(allow_null=True,allow_blank=True)
#     driver_id=serializers.CharField(allow_null=True,allow_blank=True)
#     email = serializers.CharField(allow_null=True, allow_blank=True)
#     store_id = serializers.CharField(allow_null=True,allow_blank=True)
#     address = serializers.CharField(allow_null=True,allow_blank=True)

    
#     class Meta:
#         model = UserMaster
#         fields = ['id','full_name','licence', 'mobile_number',"store_id","address","driver_id","email"]

#     def validate(self,attrs):
#         driver_id = attrs.get('driver_id')
#         email = attrs.get('email')
#         full_name = attrs.get('full_name')
#         licence = attrs.get('licence')
#         store_id = attrs.get('store_id')
#         mobile_number = attrs.get('mobile_number')
#         address = attrs.get('address')
#         if not driver_id:
#                 raise serializers.ValidationError({"error":"driver_id is mandatory."})

#         driver = UserMaster.objects.filter(id = int(driver_id)).last()
#         if  driver:
#             if full_name:
#                 driver.full_name = full_name
#             if licence:
#                 driver.licence = licence
#             if mobile_number:
#                 driver.mobile_number = mobile_number
#             if address:
#                 driver.address = address
#             if email:
#                 driver.email = email
#             driver.save()
#         else:
#             raise serializers.ValidationError({"error":"driver_id is invalid."})
        
#         if store_id:
#             driver_mapping = DriverVendorMapping.objects.filter(driver_id = driver_id).last()
#             driver_mapping.store_id = int(store_id)
#             driver_mapping.save()
#         return attrs
    
        

# # class UpdateUserRProfileSerializer(serializers.ModelSerializer):
# #     email = serializers.CharField(required = True,error_messages={'invalid': 'Please enter a valid email.'})
# #     mobile_number=serializers.CharField(required = True,error_messages={'invalid': 'Please enter a valid mobile number.'})
# #     company_name = serializers.CharField(required = True,error_messages={'invalid': 'Please enter the company name.'})
# #     logo = serializers.ImageField(required=False,validators=[FileExtensionValidator(['PNG','JPEG','JPG'] ) ] )
# #     # license = serializers.FileField(required=False,validators=[FileExtensionValidator(['PDF','PNG','JPEG','JPG'] )])
# #     address = serializers.CharField(required = True,error_messages={'invalid': 'Please enter the address.'})
# #     class Meta:
# #         model = UserMaster
# #         fields = [ 'email', 'mobile_number', 'company_name',"logo",'address']
        
# #     def validate(self, attrs):
# #         user_object=self.instance
# #         # print(user_object,'user_object')
# #         email = attrs.get('email')
# #         mobile_number = attrs.get('mobile_number')
# #         address = attrs.get('address')
# #         company_name = attrs.get('company_name')
# #         logo = attrs.get('logo')
# #         check_existing = UserMaster.objects.filter(email=email,is_deleted=False).last()
# #         if check_existing:
# #             if check_existing.id != user_object.id:
# #                 raise serializers.ValidationError({'error':"User with this email already exists"})
# #         check_existing = UserMaster.objects.filter(mobile_number=mobile_number,is_deleted=False).last()
# #         if check_existing:
# #             if check_existing.id != user_object.id:
# #                 raise serializers.ValidationError({"error":"User with this mobile number already exists"})
# #             if not re.match(pattern,mobile_number):
# #                 raise serializers.ValidationError({'error':'Please enter a valid mobile number.'})
# #         if user_object:
# #             user_object.email = email if email else user_object.email
# #             user_object.username = email if email else user_object.email
# #             user_object.mobile_number = mobile_number if mobile_number else user_object.mobile_number
# #             user_object.address = address if address else user_object.address
# #             user_object.save()
# #             vendor_obj = VendorMaster.objects.filter(user_id = user_object.id).last() 
# #             vendor_obj.company_name = company_name if company_name else vendor_obj.company_name
# #             vendor_obj.logo = logo if logo else vendor_obj.logo
# #             vendor_obj.save()
# #         return attrs