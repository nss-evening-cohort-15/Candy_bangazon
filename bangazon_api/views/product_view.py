from django.contrib.auth.models import User
from django.db.models import Count
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from bangazon_api.helpers import STATE_NAMES
from bangazon_api.models import Product, Store, Category, Order, Rating, Recommendation
from bangazon_api.serializers import (
    ProductSerializer, CreateProductSerializer, MessageSerializer,
    AddProductRatingSerializer, AddRemoveRecommendationSerializer)


class ProductView(ViewSet):
    @swagger_auto_schema(
        request_body=CreateProductSerializer,
        responses={
            201: openapi.Response(
                description="Returns the created product",
                schema=ProductSerializer()
            ),
            400: openapi.Response(
                description="Validation Error",
                schema=MessageSerializer()
            )
        }
    )
    def create(self, request):
        """Create a new product for the current user's store"""
        store = Store.objects.get(seller=request.auth.user)
        category = Category.objects.get(pk=request.data['categoryId'])
        try:
            product = Product.objects.create(
                name=request.data['name'],
                store=store,
                price=request.data['price'],
                description=request.data['description'],
                quantity=request.data['quantity'],
                location=request.data['location'],
                category=category
            )
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=CreateProductSerializer,
        responses={
            204: openapi.Response(
                description="No Content",
            ),
            400: openapi.Response(
                description="Validation Error",
                schema=MessageSerializer()
            ),
            404: openapi.Response(
                description="The product was not found",
                schema=MessageSerializer()
            )
        }
    )
    def update(self, request, pk):
        """Update a product"""
        category = Category.objects.get(pk=request.data['categoryId'])

        try:
            product = Product.objects.get(
                pk=pk, store__seller=request.auth.user)
            product.name = request.data['name']
            product.price = request.data['price']
            product.description = request.data['description']
            product.quantity = request.data['quantity']
            product.location = request.data['location']
            product.category = category
            product.save()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        responses={
            204: openapi.Response(
                description="No Content",
            ),
            404: openapi.Response(
                description="The product was not found",
                schema=MessageSerializer()
            )
        })
    def destroy(self, request, pk):
        """Delete a product"""
        try:
            product = Product.objects.get(pk=pk, store__seller=request.auth.user)
            product.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="The list of products",
                schema=ProductSerializer(many=True)
            )
        },
        manual_parameters=[
            openapi.Parameter(
                "number_sold",
                openapi.IN_QUERY,
                required=False,
                type=openapi.TYPE_INTEGER,
                description="Get products that have sold over this amount"
            ),
            openapi.Parameter(
                "category",
                openapi.IN_QUERY,
                required=False,
                type=openapi.TYPE_INTEGER,
                description="Get products by category"
            ),
            openapi.Parameter(
                "order_by",
                openapi.IN_QUERY,
                required=False,
                type=openapi.TYPE_STRING,
                enum=['name', 'price'],
                description="Order products by name or price"
            ),
            openapi.Parameter(
                "direction",
                openapi.IN_QUERY,
                required=False,
                type=openapi.TYPE_STRING,
                enum=['asc', 'desc'],
                description="Order by ascending or descending"
            ),
            openapi.Parameter(
                "location",
                openapi.IN_QUERY,
                required=False,
                type=openapi.TYPE_STRING,
                enum=STATE_NAMES,
                description="Get Products from based on state"
            ),
            openapi.Parameter(
                "min_price",
                openapi.IN_QUERY,
                required=False,
                type=openapi.TYPE_INTEGER,
                description="Get Products over a certain price"
            ),
        ]
    )
    def list(self, request):
        """Get a list of all products"""
        products = Product.objects.all()

        number_sold = request.query_params.get('number_sold', None)
        category = request.query_params.get('category', None)
        order = request.query_params.get('order_by', None)
        direction = request.query_params.get('direction', None)
        name = request.query_params.get('name', None)

        if number_sold:
            products = products.annotate(
                order_count=Count('orders')
            ).filter(order_count__lt=number_sold)

        if order is not None:
            order_filter = f'-{order}' if direction == 'desc' else order
            products = products.order_by(order_filter)

        if category is not None:
            products = products.filter(category__id=category)

        if name is not None:
            products = products.filter(name__icontains=name)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="The requested product",
                schema=ProductSerializer()
            ),
            404: openapi.Response(
                description="Product not found",
                schema=MessageSerializer()
            ),
        }
    )
    def retrieve(self, request, pk):
        """Get a single product"""
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        method='POST',
        responses={
            201: openapi.Response(
                description="Returns message that product was added to order",
                schema=MessageSerializer()
            ),
            404: openapi.Response(
                description="Product not found",
                schema=MessageSerializer()
            ),
        }
    )
    @action(methods=['post'], detail=True)
    def add_to_order(self, request, pk):
        """Add a product to the current users open order"""
        try:
            product = Product.objects.get(pk=pk)
            order, _ = Order.objects.get_or_create(
                user=request.auth.user, completed_on=None, payment_type=None)
            order.products.add(product)
            return Response({'message': 'product added'}, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        method='DELETE',
        responses={
            201: openapi.Response(
                description="Returns message that product was deleted from the order",
                schema=MessageSerializer()
            ),
            404: openapi.Response(
                description="Either the Product or Order was not found",
                schema=MessageSerializer()
            ),
        }
    )
    @action(methods=['delete'], detail=True)
    def remove_from_order(self, request, pk):
        """Remove a product from the users open order"""
        try:
            product = Product.objects.get(pk=pk)
            order = Order.objects.get(
                user=request.auth.user, completed_on=None)
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except Order.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        method='DELETE',
        request_body=AddRemoveRecommendationSerializer(),
        responses={
            204: openapi.Response(
                description="No content, the recommendation was deleted",
            ),
            404: openapi.Response(
                description="Either the Product or User was not found",
                schema=MessageSerializer()
            ),
        }
    )
    @swagger_auto_schema(
        method='POST',
        request_body=AddRemoveRecommendationSerializer(),
        responses={
            201: openapi.Response(
                description="No content, the recommendation was added",
            ),
            404: openapi.Response(
                description="Either the Product or User was not found",
                schema=MessageSerializer()
            )
        }
    )
    @action(methods=['post', 'delete'], detail=True)
    def recommend(self, request, pk):
        """Add or remove a recommendation for a product to another user"""
        try:
            product = Product.objects.get(pk=pk)
            customer = User.objects.get(username=request.data['username'])
        except Product.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        if request.method == "POST":
            recommendation = Recommendation.objects.create(
                product=product,
                recommender=request.auth.user,
                customer=customer
            )

            return Response(None, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            recommendation = Recommendation.objects.get(
                product=product,
                recommender=request.auth.user,
                customer=customer
            )
            recommendation.delete()

            return Response(None, status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        method='POST',
        request_body=AddProductRatingSerializer(),
        responses={
            201: openapi.Response(
                description="No content, the rating was added",
            ),

        }
    )
    @action(methods=['post'], detail=True, url_path='rate-product')
    def rate_product(self, request, pk):
        """Rate a product"""
        product = Product.objects.get(pk=pk)

        try:
            rating = Rating.objects.get(
                customer=request.auth.user, product=product)
            rating.score = request.data['score']
            rating.review = request.data['review']
            rating.save()
        except Rating.DoesNotExist:
            rating = Rating.objects.create(
                customer=request.auth.user,
                product=product,
                score=request.data['score'],
                review=request.data['review']
            )

        return Response({'message': 'Rating added'}, status=status.HTTP_201_CREATED)
