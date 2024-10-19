from rest_framework import  serializers

from api.v1.models import Products

class ProductsAllSerializer(serializers.Serializer):
    
    class Meta:
        model = Products
        fileds = '__all__'
        
        
class ProductsAddSerializer(serializers.Serializer):
        
    name = serializers.CharField()
    brand_name = serializers.CharField()
    category = serializers.CharField()
    description = serializers.CharField()
    price = serializers.FloatField()
    price = serializers.FileField()
    weight = serializers.FloatField(required=False)
    