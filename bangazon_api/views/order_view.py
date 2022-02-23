from datetime import datetime
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from bangazon_api.models import Order, PaymentType
from bangazon_api.serializers import OrderSerializer, UpdateOrderSerializer
from bangazon_api.serializers.message_serializer import MessageSerializer


class OrderView(ViewSet):

    @swagger_auto_schema(responses={
        200: openapi.Response(
            description="The list of orders for the current user",
            schema=OrderSerializer(many=True)
        )
    })
    def list(self, request):
        """Get a list of the current users orders
        """
        orders = Order.objects.filter(user=request.auth.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(responses={
        204: openapi.Response(
            description="No Content"
        ),
        404: openapi.Response(
            description="The order was not found",
            schema=MessageSerializer()
        ),
    })
    def destroy(self, request, pk):
        """Delete an order, current user must be associated with the order to be deleted
        """
        try:
            order = Order.objects.get(pk=pk, user=request.auth.user)
            order.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Order.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(method='put', request_body=UpdateOrderSerializer, responses={
        200: openapi.Response(
            description="Returns a message that the order was completed",
            schema=MessageSerializer()
        ),
        404: openapi.Response(
            description="Either the order or payment type was not found",
            schema=MessageSerializer()
        ),
    })
    @action(methods=['put'], detail=True)
    def complete(self, request, pk):
        """Complete an order by adding a payment type and completed data
        """
        try:
            order = Order.objects.get(pk=pk, user=request.auth.user)
            payment_type = PaymentType.objects.get(
                pk=request.data['paymentTypeId'], customer=request.auth.user)
            order.payment_type = payment_type
            order.completed_on = datetime.now()
            return Response({'message': "Order Completed"})
        except (Order.DoesNotExist, PaymentType.DoesNotExist) as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        method='get',
        responses={
            200: openapi.Response(
                description="Returns the current user's open order",
                schema=OrderSerializer()
            ),
            404: openapi.Response(
                description="An Open order was not found for the user",
                schema=MessageSerializer()
            ),
        }
    )
    @action(methods=['get'], detail=False)
    def current(self, request):
        """Get the user's current order"""
        try:
            order = Order.objects.get(
                completed_on=None, user=request.auth.user)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({
                'message': 'You do not have an open order. Add a product to the cart to get started'},
                status=status.HTTP_404_NOT_FOUND
            )
