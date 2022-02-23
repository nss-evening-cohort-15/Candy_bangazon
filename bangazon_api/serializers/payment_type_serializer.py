from rest_framework import serializers
from bangazon_api.models import PaymentType
class PaymentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentType
        fields = ('id', 'obscured_num', 'merchant_name', 'customer')

class CreatePaymentType(serializers.Serializer):
    acctNumber = serializers.CharField()
    merchant = serializers.CharField()
