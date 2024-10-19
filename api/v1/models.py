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



class Category(models.Model):

    name = models.CharField(max_length=20,null=False)
    status = models.BooleanField(default=False)
    image = models.ImageField(upload_to="category/")

    class Meta:
        db_table = "categorie"

class Brands(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    status = models.BooleanField(default=False)
    
    class Meta:
        db_table = "brand"


class Products(models.Model):
    name = models.CharField(max_length=50,null=False)
    brand_name = models.ForeignKey(Brands, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    created_by=models.ForeignKey(UserMaster, on_delete=models.CASCADE, related_name='created_by_product')
    created_at = models.DateTimeField(auto_now=True)
    updated_by=models.ForeignKey(UserMaster, on_delete=models.CASCADE, related_name='uploaded_by_product')    
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.FloatField()    

    class Meta:
        db_table = "products"


class ProductImages(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    image = models.FileField(upload_to='products/')
    class Meta:
        db_table = "products_images"



class Orders(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    created_by=models.ForeignKey(UserMaster, on_delete=models.CASCADE, related_name='created_by_order')
    created_at = models.DateTimeField(auto_now=True)
    updated_by=models.ForeignKey(UserMaster, on_delete=models.CASCADE, related_name='uploaded_by_order')    
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.FloatField()    

    class Meta:
        db_table = "orders"