from rest_framework import  serializers

from api.v1.models import Products

class ProductsAllSerializer(serializers.Serializer):
    
    class Meta:
        model = Products
        fileds = '__all__'