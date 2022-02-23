from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.contrib.auth.models import User

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from bangazon_api.serializers import UserSerializer, MessageSerializer, CreateUserSerializer


class ProfileView(ViewSet):
    @swagger_auto_schema(
        method='GET',
        responses={
            200: openapi.Response(
                description="The requested product",
                schema=UserSerializer()
            ),
            404: openapi.Response(
                description="User not found",
                schema=MessageSerializer()
            ),
        }
    )
    @action(methods=['GET'], detail=False, url_path="my-profile")
    def my_profile(self, request):
        """Get the current user's profile"""
        try:
            serializer = UserSerializer(User.objects.first())
            return Response(serializer.data)
        except User.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        method='PUT',
        request_body=CreateUserSerializer(),
        responses={
            204: openapi.Response(
                description="No Content, User updated successfully",
            )
        }
    )
    @action(methods=['PUT'], detail=False)
    def edit(self, request):
        """Edit the current user's profile"""
        user = request.auth.user
        user.username = request.data['username']
        user.first_name = request.data['first_name']
        user.last_name = request.data['last_name']
        if request.data.get('password', None):
            user.set_password(request.data['password'])
        user.save()

        return Response(None, status=status.HTTP_204_NO_CONTENT)
