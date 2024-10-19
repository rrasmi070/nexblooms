from rest_framework import  serializers

from api.v1.models import Orders

class OrderCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(required=False)
    weight = serializers.FloatField(required=False)
    
    
class UserOrderSerializer(serializers.Serializer):
    
    class Meta:
        model = Orders
        fields = '__all__'