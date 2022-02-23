from rest_framework import serializers
from bangazon_api.models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')
        depth = 1
