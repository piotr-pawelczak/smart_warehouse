from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from warehouse.models import Product, ProductLocation


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username', 'email']
            )
        ]


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'sku',
            'description',
            'weight',
            'is_active',
        )


class ProductLocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductLocation
        fields = (
            'id',
            'product',
            'location',
            'lot_number',
            'quantity',
        )
