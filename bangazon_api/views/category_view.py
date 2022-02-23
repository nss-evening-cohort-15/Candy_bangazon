from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from bangazon_api.models import Category
from bangazon_api.serializers import CategorySerializer


class CategoryView(ViewSet):
    @swagger_auto_schema(responses={
        200: openapi.Response(
            description="The list of categories",
            schema=CategorySerializer(many=True)
        )
    })
    def list(self, request):
        """Get a list of categories
        """
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
