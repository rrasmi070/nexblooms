import re
from rest_framework import serializers
from api.v1.models import *
from api.v1.product.utils import *
import datetime 
from django.db.models import Q
from django.db import transaction
from django.core.validators import FileExtensionValidator
from django.db.models import Q
import re
from PIL import Image
import random
import os
from django.conf import settings
import io
MAX_SIZE_MB = 2
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class GetCategoryListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductCategory
        fields =['id','name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = "__all__"

class CategoryRegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required = True,error_messages={'invalid': 'Please enter a valid name.'})
    image = serializers.ImageField(required=False,validators=[FileExtensionValidator(['PNG','JPEG','JPG'] ) ] )
    description = serializers.CharField(required = False,error_messages={'invalid': 'Please enter a description.'})

    class Meta:
        model = ProductCategory
        fields = ['name','description',"image"]
    
    def validate(self, attrs):
        name = attrs.get("name")
        data_check = ProductCategory.objects.filter(name=name, is_deleted=False).last()
        if data_check:
            raise serializers.ValidationError({"error": "Category name already exists"})
        return attrs

    def compress_image(self, image):
        """Compress the image to ensure it is less than or equal to MAX_SIZE_MB."""
        img = Image.open(image)
        img_format = img.format
        img_io = io.BytesIO()

        quality = 85
        while True:
            img_io.seek(0)
            img.save(img_io, format=img_format, quality=quality, optimize=True)
            img_size_mb = len(img_io.getvalue()) / (1024 * 1024) 
            if img_size_mb <= MAX_SIZE_MB:
                break
            quality -= 5
            if quality < 10:
                raise serializers.ValidationError({"error":"Image exceeds maximum allowed size of 2MB even after compression."})
            img_io.seek(0)
        return ContentFile(img_io.getvalue(), name=image.name)

    def create(self, validated_data):
        registered_by = self.context.get('user')
        name = validated_data.get("name")
        description = validated_data.get("description")
        image = validated_data.get("image")

        if image:
            compressed_image = self.compress_image(image)
            num = random.randint(11111111, 99999999)
            image_name = f"category_compressed_{num}.jpeg"
            image_path = os.path.join(settings.MEDIA_ROOT, 'product_category_image', image_name)

            # Ensure the directory exists
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            try:
                with open(image_path, 'wb') as f:
                    f.write(compressed_image.read())
                image_url = f"product_category_image/{image_name}"
            except Exception as e:
                raise serializers.ValidationError(f"Error saving image file: {e}")
        else:
            image_url = None

        obj = ProductCategory(
            name=name,
            description=description,
            image=image_url,
            registered_by_id=int(registered_by.id),
            is_active=True,
            is_deleted=False
        )
        obj.save()
        return obj


class CategoryUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required = True,error_messages={'invalid': 'Please enter a valid name.'})
    description = serializers.CharField(required = False,error_messages={'invalid': 'Please enter a description.'})
    image = serializers.ImageField(required=False,validators=[FileExtensionValidator(['PNG','JPEG','JPG'] ) ] )
    class Meta:
        model = ProductCategory
        fields = ['name','description',"image"]
        
    def validate(self,attrs):
        user_obj = self.context.get('user_obj')
        user_check = ProductCategory.objects.filter(id=user_obj.id).last()
        if user_check:
            obj = user_check   
            category_data= ProductCategory.objects.filter(name =attrs.get("name"), is_deleted=False).last() 
            if category_data:
                if category_data.id != user_obj.id:
                    raise serializers.ValidationError({"error":"Category already exists with this name"})          
            obj.name = attrs.get("name") if attrs.get("name")  else obj.name
            obj.description =  attrs.get("description") if attrs.get("description") else obj.description
            obj.image = attrs.get('image') if attrs.get('image') else obj.image
            obj.save()
        return attrs

class ActiveInactiveCategorySerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField()
    
    class Meta:
        model = ProductCategory
        fields = ['is_active']
        
    def validate(self,attrs):
        is_active = attrs.get("is_active")
        if is_active is None:
            raise serializers.ValidationError({"error":"is_active is mandatory."})
        return attrs

class CreateProductSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    product_category = serializers.IntegerField(required=False)
    price = serializers.CharField(required=True,allow_null=True)
    stock_quantity = serializers.CharField(required=True)
    discount = serializers.CharField(required=False,allow_null=True)
    description = serializers.CharField(required=False)
    product_image = serializers.ListField(required=True)



    class Meta:
        model = ProductMaster
        fields  = ['name','product_category','price','stock_quantity','discount','description','product_image']

    def validate(self, attrs):
        request=self.context.get('request')
        name = attrs.get('name')
        product_category = attrs.get('product_category')
        price = attrs.get('price')
        stock_quantity = attrs.get('stock_quantity')
        discount = attrs.get('discount')
        description = attrs.get('description')
        product_image = attrs.get('product_image')

    

        if product_image == ['']:
            raise serializers.ValidationError({'error': "Please provide at least one image for product."})
        
        try:
            int_price = float(price)
        except ValueError:
            raise serializers.ValidationError({"error":"Price must be an float."})
        try:
            int_stock_quantity = int(stock_quantity)
        except ValueError:
            raise serializers.ValidationError({"error":"Stock quantity must be an integer."})

        with transaction.atomic():
            product_object = ProductMaster()

            product_object.name = name
            product_object.sku_id = generate_sku_id()
            product_object.product_category_id = product_category
            product_object.price = int_price
            product_object.stock_quantity = int_stock_quantity
            product_object.discount = discount if discount else None
            product_object.description = description
            product_object.created_by_id=1
            product_object.save()

            for image in product_image[0].split(','):
                map_img_product = ProductImageMapping()
                map_img_product.product_id = product_object.id
                map_img_product.product_image = image               
                map_img_product.save()  

        return attrs
    
# class GetproductMasterSerializer(serializers.ModelSerializer):
#     product_name = serializers.SerializerMethodField()
#     category_id = serializers.SerializerMethodField()
#     category = serializers.SerializerMethodField()
#     sub_category_level_1 = serializers.SerializerMethodField()
#     sub_category_level_2 = serializers.SerializerMethodField()
#     sub_category_level_3 = serializers.SerializerMethodField()
#     sub_category_level_4 = serializers.SerializerMethodField()
#     sub_category_level_1_id = serializers.SerializerMethodField()
#     sub_category_level_2_id = serializers.SerializerMethodField()
#     sub_category_level_3_id = serializers.SerializerMethodField()
#     sub_category_level_4_id = serializers.SerializerMethodField()
#     stock_quantity = serializers.SerializerMethodField()
#     price = serializers.SerializerMethodField()
#     product_image = serializers.SerializerMethodField()
#     product_details = serializers.SerializerMethodField()
#     tax_information = serializers.SerializerMethodField()
#     discounts_and_offers_id = serializers.SerializerMethodField()
#     discounts_and_offers = serializers.SerializerMethodField()
#     user_can_review_products = serializers.SerializerMethodField()
#     shipping_method = serializers.SerializerMethodField()
#     shipping_cost = serializers.SerializerMethodField()
#     estimated_delivery_date = serializers.SerializerMethodField()
#     refund_eligibility = serializers.SerializerMethodField()
#     refund_timeline = serializers.SerializerMethodField()
#     refund_procedure = serializers.SerializerMethodField()
#     return_eligibility = serializers.SerializerMethodField()
#     return_timeline = serializers.SerializerMethodField()
#     return_procedure = serializers.SerializerMethodField()

#     shipping_method_name = serializers.SerializerMethodField()
#     shipping_cost_name = serializers.SerializerMethodField()
#     estimated_delivery_date_name = serializers.SerializerMethodField()
#     refund_eligibility_name = serializers.SerializerMethodField()
#     refund_timeline_name = serializers.SerializerMethodField()
#     refund_procedure_name = serializers.SerializerMethodField()
#     return_eligibility_name = serializers.SerializerMethodField()
#     return_timeline_name = serializers.SerializerMethodField()
#     return_procedure_name = serializers.SerializerMethodField()

#     vendor_name = serializers.SerializerMethodField()
#     vendor_company_name = serializers.SerializerMethodField()
#     vendor_contact_number = serializers.SerializerMethodField()
#     vendor_email_id = serializers.SerializerMethodField()
#     created_for = serializers.SerializerMethodField()
#     created_for_id = serializers.SerializerMethodField()
#     created_for_name = serializers.SerializerMethodField()
#     vendor_id = serializers.SerializerMethodField()
#     variations = serializers.SerializerMethodField()
#     affiliates_commission = serializers.SerializerMethodField()
#     is_affiliate_commison_set = serializers.SerializerMethodField()
#     add_product_in = serializers.SerializerMethodField()
#     store_id = serializers.SerializerMethodField()
#     # store_name = serializers.SerializerMethodField()
#     brand = serializers.SerializerMethodField()
#     brand_id = serializers.SerializerMethodField()

#     class Meta:
#         model = ProductMaster
#         fields = ['id','product_name','category_id','category','sub_category_level_1_id','sub_category_level_1','sub_category_level_2_id','sub_category_level_2','sub_category_level_3_id','sub_category_level_3','sub_category_level_4_id','sub_category_level_4','stock_quantity','price','product_image','product_details','tax_information','discounts_and_offers_id','discounts_and_offers','user_can_review_products','shipping_method','shipping_cost','estimated_delivery_date','refund_eligibility','refund_timeline','refund_procedure','return_eligibility','return_timeline','return_procedure','shipping_method_name','shipping_cost_name','estimated_delivery_date_name','refund_eligibility_name','refund_timeline_name','refund_procedure_name','return_eligibility_name','return_timeline_name','return_procedure_name','vendor_name','vendor_company_name','vendor_contact_number','vendor_email_id','target_role','created_for_name','created_for_id','created_for','vendor_id','variations','affiliates_commission','is_affiliate_commison_set','add_product_in','store_id','brand_id','brand']

#     def get_store_id(self,obj):
#         # try:
#             store=list(set(StoreProductMapping.objects.filter(product_id=obj.id,is_active=True).values_list("store_id",flat=True)))
#             a = ",".join(map(str,store))
#             return a
#         # except:
#         #     return ""
    
#     # def get_store_name(self,obj):
#     #     storeids = list(set(StoreMaster.objects.filter(is_active=True).values_list("store_name",flat=True)))
#     #     store_name = StoreMaster.objects.filter(id__in=storeids).last()
#     #     print(store_name.name,'^^^^^^^^^^^^^^^^^^^^^^^')
#     #     return store_name.name
    
#     def get_add_product_in(self,obj):
#         try:
#             return obj.add_product_in
#         except:
#             return ""
#     def get_is_affiliate_commison_set(self,obj):
#         try:
#             if obj.is_affiliate_commison_set==1:
#                 return True
#             else: 
#                 return False
#         except:
#             return ""
#     def get_affiliates_commission(self,obj):
#         try:
#             return obj.affiliates_commission 
#         except:
#             return ""
#     def get_variations(self,obj):
#         try:
#             return obj.variations 
#         except:
#             return ""
#     def get_created_for_id(self,obj):
#         try:
#             user_product=UserProductMapping.objects.filter(product=obj.id,is_active=True).first()
#             if user_product:
#                 return user_product.user.id 
#             else:
#                 return ""
#         except:
#             return ""
#     def get_created_for_name(self,obj):
#         try:
#             user_product=UserProductMapping.objects.filter(product=obj.id,is_active=True).first()
#             if user_product:
#                 return user_product.user.full_name 
#             else:
#                 return ""
#         except:
#             return ""
#     def get_created_for(self,obj):
#         try:
#             if obj.target_role=="admin":
#                 return 0 
#             elif obj.target_role=="vendor":
#                 return 1
#             else:
#                 return ""
#         except:
#             return ""
#     def get_vendor_id(self,obj):
#         try:
#             if obj.target_role=="admin":
#                 return None
#             else:
#                 user_product=UserProductMapping.objects.filter(product=obj.id,is_active=True).first()
#                 if user_product:

#                     return user_product.user.id 
#                 else:
#                     return None
#         except:
#             return None
#     def get_vendor_email_id(self,obj):
#         try:
#             if obj.target_role=="admin":
#                 return None
#             else:
#                 user_product=UserProductMapping.objects.filter(product=obj.id,is_active=True).first()
#                 if user_product:
#                     return user_product.user.email 
#                 else:
#                     return ""
#         except:
#             return ""
#     def get_vendor_contact_number(self,obj):
#         try:
#             if obj.target_role=="admin":
#                 return None
#             else:
#                 user_product=UserProductMapping.objects.filter(product=obj.id,is_active=True).first()
#                 if user_product:
#                     return user_product.user.mobile_number 
#                 else:
#                     return ""
#         except:
#             return ""
#     def get_vendor_company_name(self,obj):
#         if obj.target_role == "admin":
#             return None
#         else:
#             user=UserProductMapping.objects.filter(product_id=obj.id,is_active=True).last()
#             if user:
#                 if user.user.role_id == 3:
#                     vendor = VendorMaster.objects.filter(user_id = user.user.id).last()
                
#                     return vendor.company_name
#                 else:
#                     return ""
#             else:

#                 return ""
#     def get_vendor_name(self,obj):
#         try:
#             if obj.target_role=="admin":
#                 return None
#             else:
#                 user_product=UserProductMapping.objects.filter(product=obj.id,is_active=True).first()
#                 if user_product:
#                     return user_product.user.full_name 
#                 else:
#                     return ""
#         except:
#             return ""

#     def get_return_procedure_name(self,obj):
#         try:
#             refund_obj=ProductReturnPolicy.objects.filter(product=obj.id).first()
#             if refund_obj:
#                 if refund_obj.procedures:
#                     return refund_obj.procedures.name
#                 else:
#                     return ""
#             else:
#                 return ""
#         except:
#             return ""
#     def get_return_timeline_name(self,obj):
#         try:
#             refund_obj=ProductReturnPolicy.objects.filter(product=obj.id).first()
#             if refund_obj:
#                 if refund_obj.timeline:
#                     return refund_obj.timeline.name
#                 else:
#                     return ""
#             else:
#                 return ""
#         except:
#             return ""
#     def get_return_eligibility_name(self,obj):
#         try:
#             refund_obj=ProductReturnPolicy.objects.filter(product=obj.id).first()
#             if refund_obj:
#                 if refund_obj.eligibility:
#                     return refund_obj.eligibility.name
#                 else:
#                     return ""
#             else:
#                 return ""
#         except:
#             return ""
#     def get_refund_procedure_name(self,obj):
#         try:
#             refund_obj=ProductRefundAndCancellationPolicy.objects.filter(product=obj.id).first()
#             if refund_obj:
#                 if refund_obj.procedures:
#                     return refund_obj.procedures.name
#                 else:
#                     return ""
#             else:
#                 return ""
#         except:
#             return ""
#     def get_refund_timeline_name(self,obj):
#         try:
#             refund_obj=ProductRefundAndCancellationPolicy.objects.filter(product=obj.id).first()
#             if refund_obj:
#                 if refund_obj.timeline:
#                     return refund_obj.timeline.name
#                 else:
#                     return ""
#             else:
#                 return ""
#         except:
#             return ""
#     def get_refund_eligibility_name(self,obj):
#         try:
#             refund_obj=ProductRefundAndCancellationPolicy.objects.filter(product=obj.id).first()
#             if refund_obj:
#                 if refund_obj.eligibility:
#                     return refund_obj.eligibility.name
#                 else:
#                     return ""
#             else:
#                 return ""
#         except:
#             return ""

#     def get_estimated_delivery_date_name(self,obj):
#         try:
#             if obj.add_product_in == "offline":
#                 return ""
#             else:
#                 shipping_obj=ProductShippingInformation.objects.filter(product=obj.id).first()
#                 if shipping_obj:
#                     # return shipping_obj.estimated_delivery_date.date()
#                     if shipping_obj.estimated_delivery_date:
#                         return shipping_obj.estimated_delivery_date.name
#                     else:
#                         return ""
#                 else:
#                     return ""
#         except:
#             return ""
#     def get_shipping_cost_name(self,obj):
#         try:
#             if obj.add_product_in == "offline":
#                 return ""
#             else:
#                 shipping_obj=ProductShippingInformation.objects.filter(product=obj.id).first()
#                 if shipping_obj:
#                     if shipping_obj.shipping_costs:
#                         return shipping_obj.shipping_costs.name
#                     else:
#                         return ""
#                 else:
#                     return ""
#         except:
#             return ""
#     def get_shipping_method_name(self,obj):
#         try:
#             if obj.add_product_in == "offline":
#                 return ""
#             else:
#                 shipping_obj=ProductShippingInformation.objects.filter(product=obj.id).first()
#                 if shipping_obj:
#                     if shipping_obj.shipping_methods:
#                         return shipping_obj.shipping_methods.name
#                     else:
#                         return ""
#                 else:
#                     return ""
#         except:
#             return ""
#     def get_return_procedure(self,obj):
#         try:
#             refund_obj=ProductReturnPolicy.objects.filter(product=obj.id).first()
#             if refund_obj:
#                 if refund_obj.procedures:
#                     return refund_obj.procedures.id
#                 else:
#                     return ""
#             else:
#                 return ""
#         except:
#             return ""
#     def get_return_timeline(self,obj):
#         try:
#             refund_obj=ProductReturnPolicy.objects.filter(product=obj.id).first()
#             if refund_obj:
#                 if refund_obj.timeline:
#                     return refund_obj.timeline.id
#                 else:
#                     return ""
#             else:
#                 return ""
#         except:
#             return ""
#     def get_return_eligibility(self,obj):
#         try:
#             refund_obj=ProductReturnPolicy.objects.filter(product=obj.id).first()
#             if refund_obj:
#                 if refund_obj.eligibility:
#                     return refund_obj.eligibility.id
#                 else:
#                     return ""
#             else:
#                 return ""
#         except:
#             return ""
#     def get_refund_procedure(self,obj):
#         try:
#             refund_obj=ProductRefundAndCancellationPolicy.objects.filter(product=obj.id).first()
#             if refund_obj:
#                 if refund_obj.procedures:
#                     return refund_obj.procedures.id
#                 else:
#                     return ""
#             else:
#                 return ""
#         except:
#             return ""
#     def get_refund_timeline(self,obj):
#         try:
#             refund_obj=ProductRefundAndCancellationPolicy.objects.filter(product=obj.id).first()
#             if refund_obj:
#                 if refund_obj.timeline:
#                     return refund_obj.timeline.id
#                 else:
#                     return ""
#             else:
#                 return ""
#         except:
#             return ""
#     def get_refund_eligibility(self,obj):
#         try:
#             refund_obj=ProductRefundAndCancellationPolicy.objects.filter(product=obj.id).first()
#             if refund_obj:
#                 if refund_obj.eligibility:
#                     return refund_obj.eligibility.id
#                 else:
#                     return ""
#             else:
#                 return ""
#         except:
#             return ""

#     def get_estimated_delivery_date(self,obj):
#         try:
#             if obj.add_product_in == "offline":
#                 return ""
#             else:
#                 shipping_obj=ProductShippingInformation.objects.filter(product=obj.id).first()
#                 if shipping_obj:
#                     # return shipping_obj.estimated_delivery_date.date()
#                     if shipping_obj.estimated_delivery_date:
#                         return shipping_obj.estimated_delivery_date.id
#                     else:
#                         return ""
#                 else:
#                     return ""
#         except:
#             return ""
#     def get_shipping_cost(self,obj):
#         try:
#             if obj.add_product_in == "offline":
#                 return ""
#             else:
#                 shipping_obj=ProductShippingInformation.objects.filter(product=obj.id).first()
#                 if shipping_obj:
#                     if shipping_obj.shipping_costs:
#                         return shipping_obj.shipping_costs.id
#                     else:
#                         return ""
#                 else:
#                     return ""
#         except:
#             return ""
#     def get_shipping_method(self,obj):
#         try:
#             if obj.add_product_in == "offline":
#                 return ""
#             else:
#                 shipping_obj=ProductShippingInformation.objects.filter(product=obj.id).first()
#                 if shipping_obj:
#                     if shipping_obj.shipping_methods:
#                         return shipping_obj.shipping_methods.id
#                     else:
#                         return ""
#                 else:
#                     return ""
#         except:
#             return ""
    
#     def get_user_can_review_products(self,obj):
#         try:
#             if obj.can_review==1:
#                 return True
#             elif obj.can_review==0:
#                 return False
#         except:
#             return ""
#     def get_discounts_and_offers_id(self,obj):
#         try:
#             if obj.discount:
#                 return obj.discount.id
#             else:
#                 return ""
#         except:
#             return ""
#     def get_discounts_and_offers(self,obj):
#         try:
#             if obj.discount:
#                 return obj.discount.discount_name
#             else:
#                 return ""
#         except:
#             return ""
#     def get_tax_information(self,obj):
#         try:
#             if obj.tax_information:
#                 return obj.tax_information
#             else:
#                 return ""
#         except:
#             return ""
#     def get_product_details(self,obj):
#         try:
#             if obj.description:
#                 return obj.description
#             else:
#                 return ""
#         except:
#             return ""
#     def get_product_name(self,obj):
#         try:
#             if obj.name:
#                 return obj.name
#             else:
#                 return ""
#         except:
#             return ""
#     def get_category_id(self,obj):
#         try:
#             if obj.product_category:
#                 return obj.product_category.id
#             else:
#                 return ""
#         except:
#             return ""
#     def get_category(self,obj):
#         try:
#             if obj.product_category:
#                 return obj.product_category.name
#             else:
#                 return ""
#         except:
#             return ""
#     def get_sub_category_level_1_id(self,obj):
#         try:
#             sub_category=ProductCategoryMapping.objects.filter(product=obj.id).first()
#             if sub_category:
#                 return sub_category.Level_1.id
#             else:
#                 return ""
#         except:
#             return ""
#     def get_sub_category_level_2_id(self,obj):
#         try:
#             sub_category=ProductCategoryMapping.objects.filter(product=obj.id).first()
#             if sub_category:
#                 return sub_category.Level_2.id
#             else:
#                 return ""
#         except:
#             return ""
#     def get_sub_category_level_3_id(self,obj):
#         try:
#             sub_category=ProductCategoryMapping.objects.filter(product=obj.id).first()
#             if sub_category:
#                 return sub_category.Level_3.id
#             else:
#                 return ""
#         except:
#             return ""

#     def get_sub_category_level_4_id(self,obj):
#         try:
#             sub_category=ProductCategoryMapping.objects.filter(product=obj.id).first()
#             if sub_category:
#                 return sub_category.Level_4.id
#             else:
#                 return ""
#         except:
#             return ""
#     def get_sub_category_level_1(self,obj):
#         try:
#             sub_category=ProductCategoryMapping.objects.filter(product=obj.id).first()
#             if sub_category:
#                 return sub_category.Level_1.name
#             else:
#                 return ""
#         except:
#             return ""
#     def get_sub_category_level_2(self,obj):
#         try:
#             sub_category=ProductCategoryMapping.objects.filter(product=obj.id).first()
#             if sub_category:
#                 return sub_category.Level_2.name
#             else:
#                 return ""
#         except:
#             return ""
#     def get_sub_category_level_3(self,obj):
#         try:
#             sub_category=ProductCategoryMapping.objects.filter(product=obj.id).first()
#             if sub_category:
#                 return sub_category.Level_3.name
#             else:
#                 return ""
#         except:
#             return ""

#     def get_sub_category_level_4(self,obj):
#         try:
#             sub_category=ProductCategoryMapping.objects.filter(product=obj.id).first()
#             if sub_category:
#                 return sub_category.Level_4.name
#             else:
#                 return ""
#         except:
#             return ""

#     def get_stock_quantity(self,obj):
#         try:
#             inventory_obj=InventoryMaster.objects.filter(product=obj.id).first()
#             if inventory_obj:
#                 return inventory_obj.quantity
#             elif obj.stock_quantity:
#                 return obj.stock_quantity
#             else:
#                 return ""
#         except:
#             return ""
#     def get_price(self,obj):
#         try:
#             if obj.price:
#                 return obj.price
#             else:
#                 return ""
#         except:
#             return ""

#     def get_product_image(self,obj):
#         try:
#             request = self.context.get('request')
#             base_url = request.build_absolute_uri('/')[:-1]+str('/media/')
#             image_obj=ProductImageMapping.objects.filter(product=obj.id).values('product_image')
#             image_obj_list=[]
#             if image_obj:
#                 for i in range(len(image_obj)):
#                     image_obj_list.append(str(base_url) + str(image_obj[i]['product_image']))
#                 return image_obj_list
#             else:
#                 return []
#         except:
#             return []
        
#     def get_brand(self,obj):
#         try:
#             if obj.brand:
#                 return obj.brand.name
#             else:
#                 return ""
#         except:
#             return ""
        
#     def get_brand_id(self,obj):
#         try:
#             if obj.brand:
#                 return obj.brand.id
#             else:
#                 return ""
#         except:
#             return ""
