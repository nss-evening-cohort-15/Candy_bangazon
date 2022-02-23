from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from bangazon_api.serializers import CreateUserSerializer


@swagger_auto_schema(method='POST', request_body=CreateUserSerializer, responses={
    200: openapi.Response(
        description="Returns the newly created token",
        schema=AuthTokenSerializer()
    )
})
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    '''Handles the creation of a new user for authentication
    '''

    new_user = User.objects.create_user(
        username=request.data['username'],
        password=request.data['password'],
        first_name=request.data['first_name'],
        last_name=request.data['last_name']
    )

    token = Token.objects.create(user=new_user)
    data = {'token': token.key}
    return Response(data)
