from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from bangazon_api.models import PaymentType
from bangazon_api.serializers import (
    PaymentTypeSerializer, MessageSerializer, CreatePaymentType)


class PaymentTypeView(ViewSet):
    @swagger_auto_schema(responses={
        200: openapi.Response(
            description="The list of payment types for the current user",
            schema=PaymentTypeSerializer(many=True)
        )
    })
    def list(self, request):
        """Get a list of payment types for the current user"""
        payment_types = PaymentType.objects.all()
        serializer = PaymentTypeSerializer(payment_types, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=CreatePaymentType,
        responses={
            201: openapi.Response(
                description="Returns the created payment type",
                schema=PaymentTypeSerializer()
            ),
            400: openapi.Response(
                description="Validation Error",
                schema=MessageSerializer()
            )
        }
    )
    def create(self, request):
        """Create a payment type for the current user"""
        try:
            payment_type = PaymentType.objects.create(
                customer=request.auth.user,
                merchant_name=request.data['acctNumber'],
                acct_number=request.data['merchant']
            )
            serializer = PaymentTypeSerializer(payment_type)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        responses={
            204: openapi.Response(
                description="No content, payment type deleted successfully",
            ),
            404: openapi.Response(
                description="Payment type not found",
                schema=MessageSerializer()
            )
        }
    )
    def delete(self, request, pk):
        """Delete a payment type"""
        try:
            payment_type = PaymentType.objects.get(pk=pk)
            payment_type.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except PaymentType.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
