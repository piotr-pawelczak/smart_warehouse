from rest_framework.generics import UpdateAPIView, CreateAPIView
from rest_framework.viewsets import ModelViewSet

from .serializers import UserSerializer, ProductSerializer, ProductLocationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.contrib.auth.models import User
from warehouse.models import Product, ProductLocation, Location
from rest_framework import generics

# Create your views here.


class UserRecordView(APIView):
    """
    API View to create or get a list of all the registered
    users. GET request returns the registered users whereas
    a POST request allows to create a new user.
    """

    def get(self, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class ProductRecordView(APIView):

    def get(self, format=None):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductLocationRecordView(APIView):

    def get(self, format=None):
        product_locations = ProductLocation.objects.all()
        serializer = ProductLocationSerializer(product_locations, many=True)
        return Response(serializer.data)


class ProductLocationDetail(APIView):

    def get(self, request):
        product = self.request.query_params.get('product')
        lot_number = self.request.query_params.get('lot_number')
        location = self.request.query_params.get('location')

        product_location = ProductLocation.objects.get(product_id=product, lot_number=lot_number, location=location)
        serializer = ProductLocationSerializer(product_location, many=False)
        return Response(serializer.data)


class ProductLocationUpdate(UpdateAPIView):
    queryset = ProductLocation.objects.all()
    serializer_class = ProductLocationSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.quantity = request.data.get("quantity")
        instance.save()

        serializer = ProductLocationSerializer(instance)
        return Response(serializer.data)


class ProductLocationCreate(CreateAPIView):
    serializer_class = ProductLocationSerializer
    permission_classes = (IsAuthenticated,)










