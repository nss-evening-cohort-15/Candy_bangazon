from rest_framework import serializers
from bangazon_api.models import Order
from bangazon_api.models.payment_type import PaymentType


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'products', 'created_on', 'completed_on', 'total')
        depth = 1

class UpdateOrderSerializer(serializers.ModelSerializer):
    paymentTypeId = serializers.IntegerField()

    class Meta:
        model = PaymentType
        fields = ('paymentTypeId',)
