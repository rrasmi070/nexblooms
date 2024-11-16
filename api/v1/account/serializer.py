import re
import random
import string
import datetime
from django.db import transaction
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from rest_framework import serializers
from api.v1.account.utils import *
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


class TempWebUserRegisterSerializer(serializers.ModelSerializer):
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
    
    password = serializers.CharField(
        required=True,
        error_messages={'invalid': 'Please enter the password.'}
    )
   

    class Meta:
        model = UserMaster
        fields = ['id', 'first_name', 'last_name', 'mobile_number', 'email',  'password']

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
        password = attrs.get('password')

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

        # Create and save the new user
        with transaction.atomic():
            user = UserMaster(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=email,
                mobile_number=mobile_number,
                # country=country,
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

class RefreshTokenSerializer(serializers.ModelSerializer):
    access_token = serializers.CharField(required=True,error_messages={'blank': 'Please enter access_token'})
    class Meta:
        model = UserMaster
        fields=['access_token']
    def validate(self, attrs):
        access_token = attrs.get('access_token')
        try:
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError as e:
            raise serializers.ValidationError({'error': 'Expired access token, please login again.'})
        user = UserMaster.objects.filter(id=payload.get('user_id')).first()
        if user is None:
            raise serializers.ValidationError({'error' : 'User not found'})
        if not user.is_active:
            raise serializers.ValidationError({'error' : 'User is inactive'})
        return attrs
    


class WebUserLoginSerializer(serializers.Serializer):
    email= serializers.CharField(max_length=100)
    password= serializers.CharField(max_length=100)
    remember_me= serializers.BooleanField(default=True)
    class Meta:
        model = UserMaster
        fields = ['email', 'password',"remember_me"]

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user_check = UserMaster.objects.filter(Q(username = email),is_deleted=False).last()
        if not user_check:
            raise serializers.ValidationError({'error':"The entered email doesn't exist"})
        if not user_check.is_active:
            raise serializers.ValidationError({'error':'Your Account is inactive.'})
        
        if not (user_check.check_password(password)):
            raise serializers.ValidationError({'error':'You have entered wrong password.'})
        return attrs
    

class WebUserDetailsSerialzier(serializers.ModelSerializer):
    access_token = serializers.SerializerMethodField()
    refresh_token = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = UserMaster
        fields = ['id','first_name','last_name','full_name','email','mobile_number','username','role','is_active','is_email_verified','is_mobile_verified','access_token','refresh_token']
    
    def get_role(self,obj):
        return obj.role.role

    def get_access_token(self, obj): 
        remember_me = self.context.get('remember_me')
        return get_web_access_tokens_for_user(obj.id,remember_me)

    def get_refresh_token(self, obj):
        remember_me = self.context.get('remember_me')
        return get_web_refresh_tokens_for_user(obj.id,remember_me)


# Sent OTP for forgot Password
class SentOTPForgetPasswordSerializer(serializers.Serializer):
    email= serializers.CharField(max_length=100, required=False,allow_blank=True)
    mobile_number= serializers.CharField(max_length=100,  required=False,allow_blank=True)
    
    
    class Meta:
        # model = UserMaster
        fields = ['mobile_number', 'email']

    def validate(self, attrs):
        email = attrs.get('email')
        mobile_number = attrs.get('mobile_number')

        if not email and not mobile_number:
            raise serializers.ValidationError({'error':'Please provide email or mobile number.'})
        

        if email:
            if not UserMaster.objects.filter(email=email).exists():
                raise serializers.ValidationError({"error":'This email address is not registered with us.'})
            if not UserMaster.objects.filter(email=email, is_active=True, is_deleted=False).exists():
                raise serializers.ValidationError({"error":'You are not allowed to login.'})
            
        if mobile_number:
            if not UserMaster.objects.filter(mobile_number=mobile_number).exists():
                raise serializers.ValidationError({"error":'This mobile number is not registered with us.'})
            if not UserMaster.objects.filter(mobile_number=mobile_number, is_active=True, is_deleted=False).exists():
                raise serializers.ValidationError({"error":'You are not allowed to login.'})
        

        return attrs

class ForgetPasswordSerializer(serializers.Serializer):
    email= serializers.CharField(max_length=100, required=False)
    mobile_number= serializers.CharField(max_length=100, required=False)
    otp = serializers.CharField(max_length=4, required=False)
    password= serializers.CharField(max_length=100, required=False)
    confirm_password= serializers.CharField(max_length=100, required=False)
    
    class Meta:
        # model = UserMaster
        fields = ['mobile_number', 'email','password','confirm_password']

    def validate(self, attrs):
        email = attrs.get('email')
        mobile_number = attrs.get('mobile_number')
        otp = attrs.get('otp')
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if not email and not mobile_number:
            raise serializers.ValidationError({'error':'Please provide email or mobile number.'})
        
        if email:
            if not UserMaster.objects.filter(email=email).exists():
                raise serializers.ValidationError({"error":'This email address is not registered wiht us.'})
            if not UserMaster.objects.filter(email=email, is_active=True, is_deleted=False).exists():
                raise serializers.ValidationError({"error":'You are not allowed to login.'})
            if UserMaster.objects.filter(email=email, is_active=True, is_deleted=False).last().email_otp != otp:
                raise serializers.ValidationError({"error":'Entered otp is not correct..'})
            
            time = otp_email_time_generate(UserMaster.objects.filter(email=email, is_active=True, is_deleted=False).last())
            print(time, datetime.datetime.now())
            
            if not (time >=0 and time <=10):
                raise serializers.ValidationError({"error":'Otp Is Expired, please generate again.'})


            
        if mobile_number:
            if not UserMaster.objects.filter(mobile_number=mobile_number).exists():
                raise serializers.ValidationError({"error":'This mobile number is not registered wiht us.'})
            
        if not password and not confirm_password:
            raise serializers.ValidationError({"error":'Password and confirm password is mandatory'})
        
        if password != confirm_password:
            raise serializers.ValidationError({"error":'Password and confirm password does not match.'})

        return attrs

class ChangePasswordConfirmationGenericsSerializer(serializers.Serializer):
    password= serializers.CharField(max_length=100, required=False)
    confirm_password= serializers.CharField(max_length=100, required=False)
    
    class Meta:
        # model = UserMaster
        fields = ['password','confirm_password']
        
    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')   

      
        if not password and not confirm_password:
            raise serializers.ValidationError({"error": 'Password and confirm password are mandatory'})

      
        password_regex = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-+=/_]).{8,}$"

        
        if not bool(re.fullmatch(password_regex, attrs['password'])):
            raise serializers.ValidationError({'error': "Password must be 8 characters long, alphanumeric, and must contain special characters"})

   
        if password != confirm_password:
            raise serializers.ValidationError({"error": 'Password and confirm password do not match.'})

        return attrs



class SingleUserDetailsSerializer(serializers.ModelSerializer):
    access_token = serializers.SerializerMethodField()
    refresh_token = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = UserMaster
        fields = ['id','first_name','last_name','full_name','email','mobile_number','username','role','is_active','is_email_verified','is_mobile_verified','access_token','refresh_token']
    
    
    def get_role(self,obj):
        if obj.role.role:   
            return obj.role.role
        else:
            return None

    def get_access_token(self, obj): 
        remember_me = self.context.get('remember_me')
        return get_access_tokens_for_user(obj.id,remember_me)

    def get_refresh_token(self, obj):
        remember_me = self.context.get('remember_me')
        return get_refresh_tokens_for_user(obj.id,remember_me)
    

class ProfileWEBUpdateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=250,required=False,allow_null=True)
    email = serializers.CharField(max_length=250,required=False,allow_null=True)
    mobile_number = serializers.CharField(max_length=250,required=False,allow_null=True)
    address = serializers.CharField(required=False,allow_null=True)


    class Meta:
        model = UserMaster
        fields = ['full_name','email','mobile_number','address']
        
    def validate(self,attrs):
        user = self.context.get('user')
        user_instance = self.instance
        full_name = attrs.get('full_name')
        email = attrs.get('email',None)
        address = attrs.get('address',None)

        val_email=UserMaster.objects.filter(email__iexact=email,is_deleted=False).last()
        if val_email:
            if val_email.id != user.id:
                raise serializers.ValidationError({'error':'email already exists.'})
        
        mobile_number = attrs.get('mobile_number')
        val_mobile_number=UserMaster.objects.filter(mobile_number__iexact=mobile_number,is_deleted=False).last()
        if val_mobile_number:
            if val_mobile_number.id != user.id:
                raise serializers.ValidationError({'error':'mobile_number already exists.'})
                
        user_instance.full_name = full_name if full_name else user_instance.full_name
        user_instance.first_name = full_name.split(" ")[0] if full_name else user_instance.first_name
        user_instance.last_name = ' '.join(full_name.split(" ")[1:]) if full_name and len(full_name.split(" ")) > 1 else ""
        user_instance.email = email if email else user_instance.email
        user_instance.username = email if email else user_instance.email
        user_instance.mobile_number = mobile_number if mobile_number else user_instance.mobile_number
        user_instance.address = address if address else user_instance.address

        user_instance.save()
        attrs['id']=self.instance
        return attrs
    

class ShowProfileWEBUpdateSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    mobile_number = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()


    class Meta:
        model = UserMaster
        fields = ['full_name','email','mobile_number','country']

    def get_full_name(self,obj):
        try:
            return obj.full_name
        except:
            return ""
    def get_email(self,obj):
        try:
            return obj.email
        except:
            return ""
    def get_mobile_number(self,obj):
        try:
            return obj.mobile_number
        except:
            return ""
    def get_country(self,obj):
        try:
            return obj.countrymaster.id
        except:
            return ""
        
    # def get_image(self,obj):
    #     request = self.context.get('request')
    #     base_url = request.build_absolute_uri('/')[:-1]+str('/media/')
    #     try:
    #         return str(base_url)+str(obj.image)
    #     except:
    #         return ""

