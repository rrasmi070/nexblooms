from django.db import models
from django.contrib.auth.models import  AbstractBaseUser
from api.v1.manager import CustomUserManager 
# Create your models here.









class Role(models.Model):
    ADMIN = 1
    SUB_ADMIN = 2
    USER = 3
    ROLE_CHOICES = [(ADMIN, 'ADMIN'),(SUB_ADMIN ,'SUB_ADMIN'),(USER, 'USER'),]
    role = models.CharField(max_length=20,null=False, choices=ROLE_CHOICES,)

    class Meta:
        db_table = "user_roles"




class CountryMaster(models.Model):
    code = models.CharField(max_length=50,null=True)
    flag = models.URLField(max_length=200,null=True)
    flag_image = models.ImageField(null=True, upload_to = "country/flag/")
    currency_symbol = models.CharField(max_length=50,null=True)
    currency_code = models.CharField(max_length=10,null=True)
    currency_name = models.CharField(max_length=100,null=True)
    short_name = models.CharField(max_length=10,null=True)
    name =models.CharField(max_length=50)
    is_active=models.BooleanField(default=False)
    is_deleted=models.BooleanField(default=False)
    created_on=models.DateTimeField(auto_now_add=True)
    updated_on=models.DateTimeField(blank=True,null=True)
    class Meta:
        db_table = 'country_master'




class UserMaster(AbstractBaseUser):
    first_name = models.CharField(max_length=250,null=True)
    last_name = models.CharField(max_length=250,null=True)
    full_name = models.TextField(null=True)
    username = models.CharField(max_length=250,unique=True)
    email = models.EmailField(max_length=250)
    image = models.ImageField(null=True, upload_to = "profile_image/")
    mobile_number = models.CharField(max_length=16)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)
    is_email_verified = models.BooleanField(default=False)
    mobile_otp =  models.CharField(max_length=4, null=True, blank=True)
    email_otp =  models.CharField(max_length=4, null=True, blank=True)
    mobile_otp_generate_time = models.DateTimeField( blank=True,null=True)
    email_otp_generate_time = models.DateTimeField( blank=True,null=True)
    country = models.CharField(max_length=250,null=True)
    countrymaster = models.ForeignKey(CountryMaster, on_delete=models.CASCADE, null=True)
    raw_password = models.CharField(max_length=250, null=True)
    address = models.TextField(null=True)  
    is_mobile_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_by = models.CharField(max_length=100,null=True)
    bio = models.TextField(null=True)
    fcm_token = models.TextField(null=True)
    is_password_changed = models.BooleanField(default=False)
    is_access_updated = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    registered_by = models.ForeignKey('UserMaster', on_delete=models.CASCADE, null=True, blank=True)
    is_approved=models.CharField(max_length=100,null=True,blank=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = "user_master"
        indexes = [
            models.Index(fields=['email','mobile_number','id']),
        ]


class AppUserTokens(models.Model):
    user = models.ForeignKey(UserMaster, on_delete=models.CASCADE, null=True)
    token = models.TextField(null=True)
    created_on = models.DateTimeField(auto_now_add=True)



class ProductCategory(models.Model):
    name = models.CharField(max_length=100,null=True)
    image = models.ImageField(null=True, upload_to = "product_category_image/")
    description = models.TextField(null=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    registered_by = models.ForeignKey('UserMaster', on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = "product_category_master"
        indexes = [
            models.Index(fields=['name']),
        ]


class ProductMaster(models.Model):
    name = models.CharField(max_length=250,null=True,blank=True)
    sku_id = models.CharField(max_length=100,null=True, blank=True)
    price = models.CharField(max_length=20,null=True,blank=True)
    stock_quantity = models.CharField(max_length=250,null=True,blank=True)
    product_category = models.ForeignKey(ProductCategory,on_delete=models.CASCADE,null=True,blank=True)
    discount = models.CharField(max_length=250,null=True,blank=True)
    created_by = models.ForeignKey(UserMaster, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
 
    class Meta:
        db_table = "product_master"
        indexes = [
            models.Index(fields=['created_by','product_category','discount']),]
 
class ProductImageMapping(models.Model):
    product_image = models.ImageField(null=True, upload_to="product_image/")
    product = models.ForeignKey(ProductMaster,on_delete=models.CASCADE,null=True,blank=True)
 
    class Meta:
        db_table = "product_image_mapping"
        indexes = [
            models.Index(fields=['product']),]
        

class Cart(models.Model):    
    product = models.ForeignKey(ProductMaster,on_delete=models.CASCADE,null=True)
    user = models.ForeignKey(UserMaster,on_delete=models.CASCADE,null=True,blank=True)
    product_type=models.CharField(max_length=50,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)    
    delivery_type = models.CharField(max_length=50,null=True,blank=True)    
    quantity = models.IntegerField(null=True,blank=True)
    created_on  =  models.DateTimeField(auto_now_add=True, blank=True,null=True)
    updated_on  =  models.DateTimeField(auto_now=True)    
    class Meta:
        db_table = 'cart'
        models.Index(fields=['user'])

class WishlistMaster(models.Model):
    user = models.ForeignKey(UserMaster,on_delete=models.CASCADE,null=True)
    product=models.ForeignKey(ProductMaster,on_delete=models.CASCADE,null=True)
    type=models.CharField(max_length=50,null=True)
    is_wishlist = models.BooleanField(default=False)
    delivery_type = models.CharField(max_length=50,null=True,blank=True)    
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on  =  models.DateTimeField(auto_now=True)
 
    class Meta:
        db_table = 'wishlist_master'